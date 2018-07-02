''' 
This module is home to the Scheduler class. 

@author: Cory Banack
'''

import clr
import log

clr.AddReference('System')
from System.Threading import Monitor, Thread, ThreadStart

# =============================================================================     
class Scheduler(object):
   '''
   A class that maintains its own thread, which can be used to invoke "tasks"
   (methods) in serial, last-in-ignore-everything-else order.  That means 
   that, in addition to the currently running task, if any, there can be at 
   most one other task (the most recently submitted one) queue up to run next.
   Queueing a large number of tasks in a short period of time will lead to the
   first, last, and an indeterminate number of the rest actually getting run.
   
   Do not forget to call the 'shutdown' method on any instance of this class 
   once it will no longer be used, so that its background thread can be safely
   disposed of.
   '''
   
   # ==========================================================================
   def __init__(self):
      
      # the next scheduled task.  if this is "self", it means that the next
      # scheduled task is to shut down the __scheduler's background thread.
      self.task = None;
      
      # the background thread that tasks get run on
      self.loop_thread = self.__start_thread_loop()
      
   # ==========================================================================
   def submit(self, task):
      '''
      Submits the given task (a method handle) to this Scheduler, to be run on 
      the background thread. if the Scheduler is idle, the given task will be 
      run almost immediately.  If the Scheduler is busy, the given task will be 
      run as soon as the Scheduler finishes its current task, UNLESS a new task 
      is added before the given task has a chance to start.  In that case, the 
      new task will take the given task's place in line, and the given task will
      never be executed. 
      
      If this Scheduler has been shutdown, the given task will never be run.
      '''
       
      if task:
         Monitor.Enter(self)
         try:
            if self.task != self:
               # notice this replace any task that is waiting to be run
               self.task = task
            Monitor.Pulse(self)
         finally:
            Monitor.Exit(self)
            
            
   # ==========================================================================            
   def shutdown(self, block):
      '''
      Shuts down this Scheduler, after it has finished any task that it may 
      currently be running.  After this method is called, no further submitted 
      tasks will be run by this Scheduler, ever.  You MUST call this method in
      order to clean up this Scheduler properly.
      
      The 'block' boolean parameter indicates whether this method should block 
      until the Scheduler thread has finished running any last task
      and shutting down (true), or should return immediately (false).  
      '''
      
      self.submit(self) # submitting "self" is a magic trick that shuts down
      if block:
         self.loop_thread.Join()
      
      
   # ==========================================================================               
   def __start_thread_loop(self):
      '''
      Starts (and returns) the background thread, which will wait-loop forever,
      running tasks that are submitted via the 'submit' method, until it is 
      flagged by the 'shutdown' method to terminate.   
      '''
      
      def threadloop():
         task = None
         while task != self:
            try:
               Monitor.Enter(self)
               try:
                  task = self.task
                  if task != self:
                     self.task = None
                  if task is None:
                     Monitor.Wait(self)
               finally:
                  Monitor.Exit(self)
                  
               if task != self and task is not None:
                  task()
                        
            except Exception as ex:
               # slightly odd error handling, cause this thread should NEVER
               # die as the result of an exception!
               try: log.handle_error(ex) 
               except: pass
               task = None
               
      thread = Thread(ThreadStart(threadloop))
      thread.IsBackground = True
      thread.Start()
      return thread
