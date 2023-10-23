import os
from flask import Flask, request, render_template
from moviepy.editor import ImageClip, TextClip, VideoFileClip, CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    first_uploaded_image = request.files['image']
    uploaded_video = request.files['video']
    video_text = request.form['videoText'].split('\n')
    second_uploaded_image = request.files['secondImage']
    second_image_text = request.form['secondImageText'].split('\n')

    if first_uploaded_image:
        first_image_video_path="first_output_video.mp4"
        create_video_from_image(first_uploaded_image, "first_uploaded_image_path.png", output_video_duration=5, output_video_fps=30, output_video_path=first_image_video_path)
    else:
        return "The first image upload has failed"

    if uploaded_video:
        video_path = "second_output_video.mp4"
        uploaded_video.save(video_path)
        add_text_to_video(video_path , video_text)
    else:
        return "The video clip upload has failed"

    if second_uploaded_image:
        second_image_video_path="third_output_video.mp4"
        create_video_from_image(second_uploaded_image, "second_uploaded_image_path.png", output_video_duration=10, output_video_fps=30, output_video_path=second_image_video_path)
        add_text_to_video(second_image_video_path, second_image_text)
    else:
        return "The second image upload has failed"

    merged_video = merge_videos([first_image_video_path, video_path, second_image_video_path])

    return send_video_to_user(merged_video)

def create_video_from_image(uploaded_image, uploaded_image_path, output_video_duration, output_video_fps, output_video_path):
    # Save the uploaded image
    image_path = uploaded_image_path
    uploaded_image.save(image_path)

    # Create a video from the image
    video_duration = output_video_duration
    video = ImageClip(uploaded_image_path, duration=video_duration)

    # Set the frames per second (fps) for the video
    video.fps = output_video_fps

    # Set the output video file path
    output_path = output_video_path

    # Write the video to the output file
    video.write_videofile(output_path, codec='libx264')

def add_text_to_video(video_path, text_lines):
    video = VideoFileClip(video_path)
    duration = video.duration
    line_duration = duration / len(text_lines)

    final_video = CompositeVideoClip([video])

    for i, text in enumerate(text_lines):
        text_clip = TextClip(text, fontsize=24, color='white', size=video.size)
        text_clip = text_clip.set_duration(line_duration)
        text_clip = text_clip.set_start(i * line_duration)

        final_video = CompositeVideoClip([final_video, text_clip])

    final_video_path = video_path.replace('.mp4', '_with_text.mp4')
    final_video.write_videofile(final_video_path, codec='libx264')
    return final_video_path

def merge_videos(video_paths):
    clips = [VideoFileClip(path) for path in video_paths]
    merged_clip = concatenate_videoclips(clips)
    return merged_clip

def send_video_to_user(video_clip):
    # Write the merged video to a temporary file
    temp_video_path = 'merged_video.mp4'
    video_clip.write_videofile(temp_video_path, codec='libx264')

    # Send the temporary file as a response to the user
    return send_file(temp_video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)