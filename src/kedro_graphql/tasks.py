from kedro.framework.project import pipelines
from kedro.io import DataCatalog
#from kedro.runner import SequentialRunner
from kedro_graphql.runners import init_runner
from kedro_graphql.logs.logger import KedroGraphQLLogHandler
from celery import shared_task, Task
from .models import State
from datetime import datetime

#from .backends import init_backend
#from .config import RUNNER
import logging
logger = logging.getLogger("kedro")

class KedroGraphqlTask(Task):

    _db = None

    @property
    def db(self):
        if self._db is None:
            #self._db = self._app.kedro_graphql_backend
            self._db = self.app.kedro_graphql_backend
        return self._db

    def before_start(self, task_id, args, kwargs):
        """Handler called before the task starts.

        .. versionadded:: 5.2

        Arguments:
            task_id (str): Unique id of the task to execute.
            args (Tuple): Original arguments for the task to execute.
            kwargs (Dict): Original keyword arguments for the task to execute.

        Returns:
            None: The return value of this handler is ignored.
        """
        handler = KedroGraphQLLogHandler(task_id, broker_url = self._app.conf["broker_url"])
        logger.addHandler(handler)

        self.db.update(task_id=task_id, values = {"state": State.STARTED})

    def on_success(self, retval, task_id, args, kwargs):
        """Success handler.

        Run by the worker if the task executes successfully.

        Arguments:
            retval (Any): The return value of the task.
            task_id (str): Unique id of the executed task.
            args (Tuple): Original arguments for the executed task.
            kwargs (Dict): Original keyword arguments for the executed task.

        Returns:
            None: The return value of this handler is ignored.
        """
        
        self.db.update(task_id=task_id, values = {"state": State.SUCCESS})


    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry handler.

        This is run by the worker when the task is to be retried.

        Arguments:
            exc (Exception): The exception sent to :meth:`retry`.
            task_id (str): Unique id of the retried task.
            args (Tuple): Original arguments for the retried task.
            kwargs (Dict): Original keyword arguments for the retried task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        
        self.db.update(task_id=task_id, values = {"state": State.RETRY, "task_exception": str(exc), "task_einfo": str(einfo)})
   
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        
        self.db.update(task_id=task_id, values = {"state": State.FAILURE, "task_exception": str(exc), "task_einfo": str(einfo)})

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Handler called after the task returns.

        Arguments:
            status (str): Current task state.
            retval (Any): Task return value/exception.
            task_id (str): Unique id of the task.
            args (Tuple): Original arguments for the task.
            kwargs (Dict): Original keyword arguments for the task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        finished_at = datetime.now()
        self.db.update(task_id=task_id, values = {"finished_at": finished_at, "task_result": retval})

        logger.info("Closing log stream")
        for handler in logger.handlers:
            if isinstance(handler, KedroGraphQLLogHandler) and handler.topic == task_id:
                handler.flush()
                handler.close()
                handler.broker.connection.delete(task_id) ## delete stream
                handler.broker.connection.close()
        logger.handlers = []




@shared_task(bind = True, base = KedroGraphqlTask)
def run_pipeline(self, 
                 name: str = None, 
                 inputs: dict = None, 
                 outputs: dict = None, 
                 parameters: dict = None, 
                 data_catalog: dict = None,
                 runner: str = None):

    ## start
    if data_catalog:
        logger.info("using data_catalog parameter to build data catalog")
        io = DataCatalog().from_config(catalog = data_catalog)
    else:
        logger.info("using inputs and outputs parameters to build data catalog")
        logger.info("inputs: " + str(inputs))
        logger.info("outputs: " + str(outputs))
        catalog = {**inputs, **outputs}
        io = DataCatalog().from_config(catalog = catalog)

    ## add parameters to DataCatalog e.g. {"params:myparam":"value"}
    params = {"params:"+k:v for k,v in parameters.items()}
    params["parameters"] = parameters
    io.add_feed_dict(params)

    runner = init_runner(runner = runner)
    runner().run(pipelines[name], catalog = io)
    
    return "success"
