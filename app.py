from app import app, db
from app.models import User, Group, Artist, user_to_artist

if __name__ == '__main__':
    app.run(debug=True)
    
    
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'user': User, 'group': Group, 'artist': Artist, 'user_to_artist': user_to_artist}