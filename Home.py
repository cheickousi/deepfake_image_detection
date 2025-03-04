#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 11:17:
"""

import os
import random

import numpy as np
import streamlit as st
import tensorflow as tf


# prediction output
def predict_img(filename):
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    image_height = 256
    image_width = 256
    model_path = os.getcwd()

    loaded_model = tf.saved_model.load(export_dir=os.path.join(model_path, "model/base_model"), tags=['serve'])
    class_names = ['fake', 'real']

    img = tf.keras.utils.load_img(filename, target_size=(image_height, image_width))

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    predictions = loaded_model(img_array)
    score = tf.nn.softmax(predictions[0])
    d = [class_names[np.argmax(score)], round(100 * np.max(score), 2)]

    return d


# Function to resize the image
def resize_image(image, size):
    resized_image = image.resize(size)
    return resized_image


# Custom CSS
def load_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        h1, h2, h3 {
            color: #32CD32; /* Slightly darker green */
        }
        /* Styling for the active tab */
        .st-bb .st-at, .st-bb .st-ae {
            border-color: #32CD32 !important;
        }
        .st-bb .st-at {
            background-color: #32CD32 !important;
            color: white !important;
        }
        /* Styling for the inactive tab */
        .st-bb .st-ae {
            background-color: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)


def image_guessing_game():
    local_root = os.getcwd()
    # Paths to the directories containing real and fake images
    real_images_dir = local_root + '/data/valid/real'
    fake_images_dir = local_root + '/data/valid/fake'

    real_images = [img for img in os.listdir(real_images_dir) if os.path.isfile(os.path.join(real_images_dir, img))]
    fake_images = [img for img in os.listdir(fake_images_dir) if os.path.isfile(os.path.join(fake_images_dir, img))]

    # Ensure there are enough images
    if len(real_images) < 5 or len(fake_images) < 5:
        st.error("Insufficient images in directories")
        return

    selected_real_images = random.sample(real_images, 5)
    selected_fake_images = random.sample(fake_images, 5)

    all_images = selected_real_images + selected_fake_images
    random.shuffle(all_images)

    if 'current_image' not in st.session_state:
        st.session_state.current_image = 0
        st.session_state.score = 0
        st.session_state.correct_answers = {img: 'Real' if img in selected_real_images else 'Fake' for img in
                                            all_images}

    if st.session_state.current_image < len(all_images):
        image_name = all_images[st.session_state.current_image]
        image_path = os.path.join(real_images_dir if image_name in selected_real_images else fake_images_dir,
                                  image_name)

        if not os.path.exists(image_path):
            st.error(f"Image not found: {image_path}")
            return

        st.image(image_path, caption=f'Image {st.session_state.current_image + 1}')

        col1, col2 = st.columns(2)
        with col1:
            if st.button('Real', key=f'real_{st.session_state.current_image}'):
                if st.session_state.correct_answers.get(image_name) == 'Real':
                    st.success("Correct!")
                    st.session_state.score += 1
                else:
                    st.success("Incorrect! Image is Fake")
                st.session_state.current_image += 1

        with col2:
            if st.button('AI-Generated', key=f'fake_{st.session_state.current_image}'):
                if st.session_state.correct_answers.get(image_name) == 'Fake':
                    st.session_state.score += 1
                    st.success("Correct!")
                else:
                    st.success("Incorrect! Image is Real")
                st.session_state.current_image += 1

    else:
        st.write(f'Game Over! Your score: {st.session_state.score} out of {len(all_images)}')
        if st.button('Restart Game'):
            st.session_state.current_image = 0
            st.session_state.score = 0
            st.session_state.correct_answers.clear()
            random.shuffle(all_images)
            st.session_state.correct_answers = {img: 'Real' if img in selected_real_images else 'Fake' for img in
                                                all_images}


def main():
    load_css()
    st.title('Luminare')

    tab1, tab2 = st.tabs(['DeepFake Detection', 'Spot the Fake!'])

    with tab1:
        st.header("Unveil the Authentic You")
        st.markdown(
            "At Luminare, we believe in the power of truth and authenticity. In a world filled with filters and "
            "digital enhancements, it's becoming increasingly challenging to distinguish between real and fake. "
            "That's where we come in.")

        st.header("Verify the Authenticity of Your Image")

        uploaded_file = st.file_uploader("Upload an image of a human face to check if it's real or AI-generated",
                                         type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Display the uploaded image

            response = predict_img(uploaded_file)

            if response is not None:
                st.success(f'Verification Complete: The image is {response[0]} with a {response[1]} % confidence')
                st.image(uploaded_file, caption='Uploaded Image', use_column_width=True, width=10)

            else:
                st.error('Failed to verify the image')

    with tab2:
        st.header('Spot the Fake!')
        image_guessing_game()


if __name__ == "__main__":
    main()
