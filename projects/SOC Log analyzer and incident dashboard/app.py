from flask import Flask, render_template
from parse import parse_ssh_log,analyze_attempts

app=Flask(__name__)

@app.route('/')
def dashboard():
    attempts=parse_ssh_log('sample_auth.log')
    analyzer=analyze_attempts(attempts)
    return render_template('dashboard.html',data=analyzer)

if __name__=='__main__':
    app.run(debug=True)
    
    