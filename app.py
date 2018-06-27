import os
import src.getsend as getsend
import src.handler as handler

token = os.getenv('TOKEN')
sender = getsend.Sender(token)
offset = 0
while True:
    messages = getsend.getUpdates(offset, token)
    if messages == []:
        continue
    for message in messages:
        user, sent = handler.handleMessage(message)

        if isinstance(sent, str): # if sent is just a string
            print(sender.sendMessage(chat_id=user, text=sent))
        elif isinstance(sent, list): # if list is a list (contains a list of formats)
            keyboard = sender.keyboard(sent) # customized message with keys
            print(sender.sendMessage(chat_id=user, text="Choose a format", reply_markup=keyboard))
        else:
            print(sender.sendVideo(chat_id=user, video=sent))
            sent.close() # closing the file, so as to be able to remove it
        offset = max([message['update_id']]) + 1
    handler.temp_delete()
