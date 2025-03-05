from flask import current_app
from queue import Queue
from threading import Thread
from langchain_core.runnables import RunnableConfig
from app.chat.callbacks.stream import StreamingHandler

class StreamableChain:
    
    def stream(self, input):
        queue = Queue()
        handler = StreamingHandler(queue)
        config = RunnableConfig(callbacks=[handler])

        def task(app_context):
            # provides access to the application context
            app_context.push()
            self.invoke(input, config=config)
        # running this stream in a separate thread, concurrently with our while loop (concorrency)
        Thread(target=task, args=[current_app.app_context()]).start()

        while True:
            token = queue.get()
            if token is None:
                break
            yield token