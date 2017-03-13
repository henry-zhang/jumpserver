# coding: utf-8

from __future__ import absolute_import, unicode_literals
import json
import time


from django.utils import timezone
from celery import shared_task

from common.utils import get_logger, encrypt_password
from .utils.runner import AdHocRunner
from .models import TaskRecord

logger = get_logger(__file__)


@shared_task(name="get_assets_hardware_info")
def get_assets_hardware_info(self, assets):
    task_tuple = (
        ('setup', ''),
    )
    hoc = AdHocRunner(assets)
    return hoc.run(task_tuple)


@shared_task(name="asset_test_ping_check")
def asset_test_ping_check(assets):
    task_tuple = (
        ('ping', ''),
    )
    hoc = AdHocRunner(assets)
    result = hoc.run(task_tuple)
    return result['contacted'].keys(), result['dark'].keys()


@shared_task(bind=True)
def run_AdHoc(self, task_tuple, assets,
              task_name='Ansible AdHoc runner', pattern='all', record=True):

    runner = AdHocRunner(assets)
    if record:
        from .models import TaskRecord
        if not TaskRecord.objects.filter(uuid=self.request.id):
            record = TaskRecord(uuid=self.request.id,
                                name=task_name,
                                assets=','.join(asset['hostname'] for asset in assets),
                                module_args=task_tuple,
                                pattern=pattern)
            record.save()
        else:
            record = TaskRecord.objects.get(uuid=self.request.id)
            record.date_start = timezone.now()
    ts_start = time.time()
    logger.warn('Start runner {}'.format(task_name))
    result = runner.run(task_tuple, pattern=pattern, task_name=task_name)
    timedelta = round(time.time() - ts_start, 2)
    summary = runner.clean_result()
    if record:
        record.date_finished = timezone.now()
        record.is_finished = True
        record.result = json.dumps(result)
        record.summary = json.dumps(summary)
        record.timedelta = timedelta
        if len(summary['failed']) == 0:
            record.is_success = True
        else:
            record.is_success = False
        record.save()
    return summary


@shared_task(bind=True)
def push_users(self, assets, users):
    """
    user: {
        name: 'web',
        username: 'web',
        shell: '/bin/bash',
        password: '123123123',
        public_key: 'string',
        sudo: '/bin/whoami,/sbin/ifconfig'
    }
    """
    if isinstance(users, dict):
        users = [users]
    if isinstance(assets, dict):
        assets = [assets]
    task_tuple = []

    for user in users:
        # 添加用户, 设置公钥, 设置sudo
        task_tuple.extend([
            ('user', 'name={} shell={} state=present password={}'.format(
                user['username'], user.get('shell', '/bin/bash'),
                encrypt_password(user.get('password', None)))),
            ('authorized_key', "user={} state=present key='{}'".format(
                user['username'], user['public_key'])),
            ('lineinfile',
             "name=/etc/sudoers state=present regexp='^{0} ALL=(ALL)' "
             "line='{0} ALL=(ALL) NOPASSWD: {1}' "
             "validate='visudo -cf %s'".format(
                 user['username'], user.get('sudo', '/bin/whoami')
             ))
        ])
    task_name = 'Push user {}'.format(','.join([user['name'] for user in users]))
    record = TaskRecord(name=task_name,
                        uuid=self.request.id,
                        date_start=timezone.now(),
                        assets=','.join(asset['hostname'] for asset in assets))
    record.save()
    logger.info('Runner {0} start {1}'.format(task_name, timezone.now()))
    hoc = AdHocRunner(assets)
    ts_start = time.time()
    _ = hoc.run(task_tuple)
    logger.info('Runner {0} complete {1}'.format(task_name, timezone.now()))
    result_clean = hoc.clean_result()
    record.time = int(time.time() - ts_start)
    record.date_finished = timezone.now()
    record.is_finished = True

    if len(result_clean['failed']) == 0:
        record.is_success = True
    else:
        record.is_success = False
    record.result = json.dumps(result_clean)
    record.save()
    return result_clean