<template>
    <!-- Post input box -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg">
        <div class="p-4">
          <input
            v-model="newPost.title"
            type="text"
            class="p-2 w-full bg-gray-700 text-white rounded-lg mb-4"
            placeholder="Enter post title"
            required
          />
          <input
            v-model="newPost.description"
            type="text"
            class="p-2 w-full bg-gray-700 text-white rounded-lg mb-4"
            placeholder="Enter post description"
            required
          />
          <textarea
            v-model="newPost.content"
            class="p-4 w-full bg-gray-700 text-white rounded-lg"
            placeholder="Make a new post"
            required
          ></textarea>
        </div>

        <div class="p-4 border-t border-gray-700 flex justify-between">
          <div class="flex items-center">
            <label for="visibility" class="mr-2">Visibility:</label>
            <select
              v-model="newPost.visibility"
              id="visibility"
              class="bg-gray-600 text-white rounded-lg px-2 py-1"
            >
              <option value="PUBLIC">Public</option>
              <option value="UNLISTED">Unlisted</option>
              <option value="FRIENDS">Friends</option>
            </select>
          </div>

          <div class="flex items-center">
            <label for="format" class="mr-2">Format:</label>
            <select
              v-model="newPost.format"
              id="format"
              class="bg-gray-600 text-white rounded-lg px-2 py-1"
            >
              <option value="text/plain">Standard</option>
              <option value="text/markdown">CommonMark</option>
              <option value="image/jpeg;base64">JPEG</option>
              <option value="image/png;base64">PNG</option>
            </select>
          </div>
        </div>
        <div class="p-4 border-t border-gray-700 flex justify-between">
        <div class="flex items-center">
            <label for="format" class="mr-2">Picture:</label>
            <input
              type="file"
              @change="handleFileUpload"
              ref="fileInput"
              class="bg-gray-600 text-white rounded-lg px-2 py-1"
            />
        </div>
        <button
            @click="createPost"
            class="inline-block py-3 px-6 bg-purple-600 text-white rounded-lg hover:bg-purple-500">
            Post
          </button>
        </div>
      </div>
</template>

<script setup>
import { useAuthorStore } from "../../stores/user";
import { ref, inject } from "vue";
import api from '../services/api';
import { useToast } from 'vue-toastification';

const toast = useToast();
const posts = inject('posts');
const authorStore = useAuthorStore();
const fileInput = ref(null);
const newPost = ref({
    title: "",
    description: "",
    content: "",
    visibility: "PUBLIC",
    format: "text/plain",
    likes: 0,
    image: null,
});

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  const maxFileSize = 10 * 1024 * 1024; // 10 MB
  if (file) {
    if (file.size > maxFileSize) {
      toast.error("File size exceeds 5MB limit.");
      event.target.value = ''; // Clear the input
      return;
    }
    newPost.value.image = file;
  }
};  

const createPost = async () => {
    try {
        const token = authorStore.accessToken;
        const contentType = newPost.value.format;

        const postData = new FormData();
        postData.append('title', newPost.value.title);
        postData.append('description', newPost.value.description);
        postData.append('content', newPost.value.content);
        postData.append('visibility', newPost.value.visibility);
        postData.append('contentType', contentType);

        if (newPost.value.image) {
            postData.append('image', newPost.value.image);
        }
        console.log('Sending data:', {
            title: newPost.value.title,
            description: newPost.value.description,
            content: newPost.value.content,
            visibility: newPost.value.visibility,
            contentType: contentType,
            image: newPost.value.image
        });

        const response = await api.post(
            "/api/posts/",
            postData,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "multipart/form-data",   //"application/json",
                }
            },
        );
        
        if (response.status >= 200 && response.status < 300) {
            // Add new post to the top of the list and initialize showComments property
            posts.value.unshift({
                ...response.data,
                likes: 0
            });

            // Clear the form
            newPost.value = {
            title: "",
            description: "",
            content: "",
            visibility: "PUBLIC",
            format: "text/plain",
            image: null,
            likes: 0
            };

            if (fileInput.value) {
                fileInput.value.value = null;
            }
        }
    } catch (error) {
        if (error.response && error.response.status === 401) {
            await refreshToken(authorStore);
            await createPost();
        } else {
            console.error("Error creating post", error);
        }
    }
};
</script>