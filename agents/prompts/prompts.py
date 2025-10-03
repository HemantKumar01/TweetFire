def OPEN_CHROME_GOOGLE_TRENDS_GOAL():
    prompt = """
1. Open Chrome browser using package name com.android.chrome
2. Navigate to Google Trends website (trends.google.com)
3. Look for trending now section in the hamburger menu
4. Find the most trending/popular topic or search term currently
5. Take note of the trending topic title and any related information
6. Return the trending topic information in JSON format as output:
{
  "trending_topic": "string",
  "description": "string",
  "category": "string"
}

Output only the JSON string, do not include any other text.
"""
    return prompt


def OPEN_GEMINI_CREATE_IMAGE_GOAL(image_prompt: str):
    prompt = f"""
1. Open Gemini app using package name com.google.android.apps.bard or open Chrome and navigate to gemini.google.com
2. If using web version, make sure you are logged into your Google account
3. In the chat interface, type the following image generation prompt: "Create an image: {image_prompt}"
4. Wait for Gemini to process and generate the image
5. Once the image is generated, look for download option or save image option
6. Download/save the generated image to the device
7. Return success status in JSON format:
{{
  "success": true,
  "message": "Image generated and downloaded successfully"
}}

Output only the JSON string, do not include any other text. Make sure to create the image with the given prompt.
"""
    return prompt


def OPEN_TWITTER_CREATE_POST_GOAL(post_content: str, has_image: bool = True):
    prompt = f"""
1. Open Twitter/X app using package name com.twitter.android
2. Make sure you are logged into your account
3. Tap on the compose tweet button (usually a plus icon or compose button)
4. Click on Post button to create a post.
5. Type the following content in the tweet composer: "{post_content}"
6. {"Add the downloaded image to the tweet by tapping the image/media button and selecting the recently downloaded image" if has_image else ""}
7. Review the tweet content and image (if applicable)
8. Tap the "Post" or "Tweet" button to publish the tweet
9. Wait for the tweet to be posted successfully
10. Return success status in JSON format:
{{
  "success": true,
  "message": "Tweet posted successfully"
}}

Output only the JSON string, do not include any other text.
"""
    return prompt
