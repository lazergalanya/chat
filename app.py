from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar-kelime'
socketio = SocketIO(app, cors_allowed_origins="*")

# Tüm bağlı kullanıcıları tutacağız: { sid: username }
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(username):
    users[request.sid] = username
    print(f"{username} bağlandı. (SID: {request.sid})")
    # Herkese güncel kullanıcı listesini gönder
    broadcast_user_list()

@socketio.on('private_message')
def handle_private_message(data):
    recipient_sid = data['recipient_sid']
    message_text = data['text']
    sender_username = users.get(request.sid, 'Bilinmeyen')
    
    payload = {
        'sender_sid': request.sid,
        'sender_name': sender_username,
        'text': message_text,
        'time': get_time()
    }
    
    # Mesajı hem alıcıya hem de gönderene (kendi ekranında da akması için) ilet
    emit('private_message', payload, room=recipient_sid)
    emit('private_message', payload, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, 'Birisi')
    print(f"{username} ayrıldı.")
    broadcast_user_list()

def broadcast_user_list():
    # Frontend'e güncel kullanıcı listesini (sid ve isimleriyle) gönderiyoruz
    user_list = [{'sid': sid, 'username': name} for sid, name in users.items()]
    emit('update_user_list', user_list, broadcast=True)

def get_time():
    from datetime import datetime
    return datetime.now().strftime('%H:%M')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)