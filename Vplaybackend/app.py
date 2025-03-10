from flask import Flask, request, jsonify
from video_routes import video_bp
from auth_routes import auth_bp
from signup_routes import signup_bp
from comment_routes import comment_bp
from user_routes import user_bp  # Import user routes
from inference import predict_proba  # Import the inference function from inference.py
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(video_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(comment_bp)  # Assuming you have a comment blueprint

# Inference route for checking if a comment is offensive
@app.route('/inference', methods=['POST'])
def inference():
    try:
        data = request.json
        comment_text = data.get('commentText')

        if not comment_text:
            return jsonify({'error': 'No commentText provided'}), 400

        # Log the received comment for debugging
        print(f"Received comment for inference: {comment_text}")

        # Use the inference function to get probabilities
        probs = predict_proba([comment_text])[0]

        # Print the probabilities to the console
        print(f"Predicted probabilities: {probs}")

        # Determine the predicted label based on the probabilities
        predicted_label = "Offensive" if probs[1] > probs[0] else "NOT Offensive"

        # Print the final predicted label
        print(f"Predicted label: {predicted_label}")
        
        return jsonify({'predictedLabel': predicted_label})

    except Exception as e:
        print(f"Error in /inference route: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use PORT from Render, default to 10000
    app.run(host="0.0.0.0", port=port)
