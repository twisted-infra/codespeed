"""
Support for benchmark reporting.
"""

from fabric.api import run, settings

from braid import git, cron, pip
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
            run('mkdir -p data')
            pip.install('Django==1.2.7')
            self.update()
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/codespeed', self.configDir)
            git.branch('https://github.com/twisted-infra/codespeed-source', '~/codespeed')

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


addTasks(globals(), Codespeed('codespeed').getTasks())
