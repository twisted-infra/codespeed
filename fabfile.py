"""
Support for benchmark reporting.
"""

from fabric.api import run, settings, env

from braid import git, cron, pip, archive, utils
from braid.twisted import service
from braid.tasks import addTasks

from braid import config


__all__ = [ 'config' ]


class Codespeed(service.Service):

    def task_install(self):
        """
        Install codespeed, a benchmark reporting tool
        """
        # Bootstrap a new service environment
        self.bootstrap()

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('mkdir -p ~/data')
            pip.install('Django==1.2.7')
            self.update()
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))
            if env.get('installTestData'):
                self.task_installTestData()

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/codespeed', self.configDir)
            git.branch('https://github.com/twisted-infra/codespeed-source', '~/codespeed')

    def djangoAdmin(self, args):
        """
        Run django-admin with proper settings.
        """
        with settings(user=self.serviceUser):
            path = '~/config:~/codespeed:~/codespeed/speedcenter'
            run('PYTHONPATH={}:$PYTHONPATH ~/.local/bin/django-admin.py {} '
                '--settings=local_settings'.format(path, ' '.join(args)))

    def task_installTestData(self):
        """
        Create test db.
        """
        self.djangoAdmin(['syncdb', '--noinput'])

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()

    def task_dump(self, localfile):
        """
        Dump codespeed database and download it to the given C{localfile}.
        """
        with settings(user=self.serviceUser):
            with utils.tempfile() as temp:
                run('sqlite3 ~/data/codespeed.db .dump >{}'.format(temp))
                archive.dump({
                    'db.dump': temp,
                }, localfile)

    def task_restore(self, localfile):
        """
        Restore codespeed database from the given C{localfile}.
        """
        msg = 'The whole database will be replaced with the backup.'

        if utils.confirm(msg):
            with settings(user=self.serviceUser):
                with utils.tempfile() as temp:
                    archive.restore({
                        'db.dump': temp,
                    }, localfile)
                    run('rm -f ~/data/codespeed.db')
                    run('sqlite3 ~/data/codespeed.db <{}'.format(temp))

addTasks(globals(), Codespeed('codespeed').getTasks())
