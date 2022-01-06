import requests
import base64


def base64encoder(images):

    images_encoded = []
    for image in images:
        try:
            image_content = requests.get(image).content
            img_b64_enc = base64.b64encode(image_content)
            img_b64_enc = img_b64_enc.decode('utf-8')
            images_encoded.append(img_b64_enc)
        except Exception as e:
            return "Error: " + str(e)

    return images_encoded


def base64decoder(images):

    images_decoded = []
    for image in images:
        try:
            img_decoded = base64.b64decode(image)
            images_decoded.append(img_decoded)
        except Exception as e:
            return "Error: " + str(e)

    return images_decoded
