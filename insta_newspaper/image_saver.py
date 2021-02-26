import requests
import re
import cv2


def save_image(name, simple_name, url, chosen_date, save_path):
    """Save an image of a given newspaper from BNF website."""

    # Getting France Soir
    daily_url = "{url}{chosen_date}".format(url=url, chosen_date=chosen_date)

    raw_response = requests.get(daily_url)

    if raw_response.status_code != 200:
        print("Bad status code:", raw_response.status_code)
        exit()

    # Search response for image source
    image_src_regex = (
        r"(https\:\/\/gallica\.bnf\.fr\/ark\:\/[0-9]+\/[0-9a-z]+\/f1\.highres)"
    )
    image_url = re.findall(image_src_regex, raw_response.text)[0]

    # Get image and save it locally
    img_response = requests.get(image_url + ".jpeg", stream=True, allow_redirects=True)

    if img_response.status_code != 200:
        print("Bad status code:", img_response.status_code)
        exit()

    image_local_save_path = "{save_path}{simple_name}-{chosen_date}.jpeg".format(
        save_path=save_path,
        simple_name=simple_name,
        chosen_date=chosen_date,
    )

    print("Image save path:", image_local_save_path)

    image = img_response.content

    with open(image_local_save_path, "wb") as out_file:
        out_file.write(img_response.content)
    del img_response

    # Format image with cv2
    image = cv2.imread(image_local_save_path)
    height, width, channels = image.shape
    # Remove watermark, source will be credited in Instagram caption
    new_height = height - 40
    image = image[0:new_height, 0:width]

    # Give image a 4:5 ratio with borders
    background_color = [37, 37, 37]
    desired_width = float(new_height) * 0.8
    border_width = int((desired_width - width) / 2)
    image = cv2.copyMakeBorder(
        image,
        0,
        0,
        border_width,
        border_width,
        cv2.BORDER_CONSTANT,
        value=background_color,
    )

    image = cv2.resize(image, (1080, 1350))

    cv2.imwrite(image_local_save_path, image)
    print("Image saved.")