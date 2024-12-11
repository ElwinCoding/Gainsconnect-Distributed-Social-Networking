<template>
  <main class="w-full bg-gray-900 min-h-screen">
    <div class="max-w-3xl mx-auto">
      <div v-if="loading" class="flex items-center justify-center min-h-screen">
        <Loader class="-ml-4"/>
      </div>
      <div v-else class="space-y-6 z-0">
        <!-- Profile Picture and Name Section -->
        <div class="flex flex-col items-center space-y-4 z-0">
          <!-- Image container with fixed dimensions -->
          <div class="w-48 h-48 relative">
            <img 
              :src="previewImage || authorStore.profileImage" 
              alt="Profile picture" 
              class="w-full h-full rounded-full object-cover"
            >
            <!-- Image upload overlay when in edit mode -->
            <div v-if="editMode">
              <!-- File upload overlay -->
              <div class="absolute inset-0 z-20">
                <input 
                  type="file" 
                  @change="onFileChange"
                  accept="image/*"
                  class="absolute inset-0 opacity-0 cursor-pointer z-20"
                />
                <div class="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center z-10">
                  <span class="text-white">Click to change image</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- URL input (outside of overlay) -->
          <div v-if="editMode" class="w-full max-w-xs">
            <input
              v-model="imageUrl"
              placeholder="Or enter image URL"
              class="w-full px-3 py-2 bg-gray-700 rounded text-white"
              @input="handleUrlInput"
            />
          </div>
          
          <!-- Display Name (editable) -->
          <div class="relative">
            <p v-if="!editMode" class="text-3xl font-bold">{{authorStore.displayName}}</p>
            <input
              v-else
              v-model="displayName"
              :placeholder="authorStore.displayName"
              class="text-3xl font-bold bg-gray-700 rounded px-2 py-1"
            />
          </div>
        </div>

        <!-- User Information -->
        <div class="space-y-4 px-4">
          <p class="text-lg">
            <span class="font-bold">Host:</span> 
            {{ host || 'No host available' }}
          </p>
          <p class="text-lg">
            <span class="font-bold">Email:</span> 
            {{ authorStore.email || 'No email available' }}
          </p>
          <!-- GitHub (editable) -->
          <div class="text-lg">
            <span class="font-bold">GitHub:</span>
            <span v-if="!editMode">
              {{ authorStore.githubUser === 'undefined' || !authorStore.githubUser ? ' No GitHub username set' : authorStore.githubUser }}
            </span>
            <input
              v-else
              v-model="githubUser"
              :placeholder="authorStore.githubUser || 'Enter GitHub username'"
              class="ml-2 bg-gray-700 rounded px-2 py-1"
            />
          </div>

          <!-- Edit/Save Buttons -->
          <div class="flex justify-center space-x-4">
            <button 
              v-if="!editMode"
              @click="editMode = true"
              class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-500 transition-colors mt-4"
            >
              Edit Profile
            </button>
            <template v-else>
              <button 
                @click="saveChanges"
                class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-500 transition-colors"
              >
                Save
              </button>
              <button 
                @click="cancelEdit"
                class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-500 transition-colors"
              >
                Cancel
              </button>
            </template>
          </div>
        </div>

        <!-- Posts Section -->
        <h2 class="text-3xl font-bold border-b-2 border-gray-600 pb-2 text-center">
            Your Posts
        </h2>
        <div v-if="posts.length > 0" class="posts-section mt-8">
          <PostCard 
            v-for="post in posts" 
            :key="post.id" 
            :post="post" 
            @delete="handleDelete" 
            class="mt-5" 
          />
        </div>
        <div v-else class="text-center mt-8 text-2xl">
          <p>✍️ You have no posts ✍️</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import PostCard from '@/components/PostCard.vue';
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useAuthorStore } from '../../stores/user';
import * as commonmark from 'commonmark';
import api from '@/services/api';
import Loader from '@/components/Loader.vue';
import { useToast } from 'vue-toastification';

// Initialize CommonMark parser and renderer
const reader = new commonmark.Parser();
const writer = new commonmark.HtmlRenderer();
const loading = ref(true);
const previewImage = ref(null);
const imageUrl = ref('');
const toast = useToast();


// saving the things locally so that we know what is going to be edidted 
const authorStore = useAuthorStore();
const encoded = encodeURIComponent(authorStore.id);
const editMode = ref(false);
const displayName = ref(authorStore.displayName);
const profileImage = ref(null);  
const githubUser = ref(authorStore.githubUser);
const host = ref();
// Ref for storing posts data
const posts = ref([]);


// Function to render content in CommonMark format
const renderCommonMark = (content) => {
  const parsed = reader.parse(content);
  return writer.render(parsed);
};

// handling  file selection for profile image upload
const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (file.size > 1024 * 1024 * 4) {
      toast.error("File size exceeds 4MB limit.");
      event.target.value = ''; // Clear the input
      return;
    }

    // create preview
    previewImage.value = URL.createObjectURL(file);
    console.log("Selected file:", file); // Debug log to see file details
    profileImage.value = file;
    imageUrl.value = '';
  }
}


// saving the updated profile information
const saveChanges = async () => {
  const formData = new FormData();
  formData.append('displayName', displayName.value);
  formData.append('github_user', githubUser.value || '');
  if (profileImage.value) {
    // if file was uploaded
    if (profileImage.value instanceof File) {
      console.log("File was uploaded:", profileImage.value); 
      formData.append('profileImage', profileImage.value, profileImage.value.name);
    }
    // if url was uploaded
    else if (typeof profileImage.value === 'string') {
      console.log("URL was uploaded:", profileImage.value); 
      formData.append('profileImage', profileImage.value);
    }
  }
  // Debug: Log each entry in FormData
  for (let [key, value] of formData.entries()) {
    console.log(`${key}: `, value);
  }

  try {
    const response = await api.post('/authors/updateProfile/', formData, {
      headers: {
        'Authorization': `Bearer ${authorStore.accessToken}`,
        'Content-Type': 'multipart/form-data',  // Important!
      }
    });
    console.log("response", response);
    authorStore.changeInfo(response.data); 
    editMode.value = false;  
  } catch (error) {
    console.error('Failed to update profile:', error);
  }
};

const handleUrlInput = () => {
  if (imageUrl.value.trim()) {
    // Basic URL validation
    if (imageUrl.value.match(/\.(jpeg|jpg|gif|png)$/i)) {
      previewImage.value = imageUrl.value;
      profileImage.value = imageUrl.value;
    } else {
      alert('Please enter a valid image URL');
    }
  }
}


// Function to retrieve public posts for the author
const fetchPublicPosts = async () => {
  try {
    // Replace `authorStore.id` with the appropriate ID to fetch posts for the currently viewed author
    const response = await api.get(`/api/authors/${encoded}/posts/`, {
      headers: {
        'Authorization': `Bearer ${authorStore.accessToken}`
      }
    });
    posts.value = response.data['src'];
    // console.log("name", authorStore.displayName);
    console.log(posts.value)
  } catch (error) {
    console.error('Failed to load posts:', error);
  }
};

// Fetch author data on component mount
onMounted(async () => {
  try {
    console.log("fetching profile data");
    const response = await api.get(`api/authors/${authorStore.uid}`, {
      headers: {
        'Authorization': `Bearer ${authorStore.accessToken}`
      }
    });
    const authorData = response.data;
    console.log("author data", response.data['host']);
    //author.value = response.data
    
    host.value = response.data['host'];
    displayName.value = authorData.displayName;
    githubUser.value = authorData.github_user;
    profileImage.value = authorData.profileImage;
    console.log("fetching posts");
    fetchPublicPosts();
    loading.value = false;
  } catch (error) {
    console.error('Failed to load profile data:', error);
  }
});

// Clean up object URL when component is destroyed
onBeforeUnmount(() => {
  if (previewImage.value && previewImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewImage.value);
  }
});

// when done with editing, just stopping 
const cancelEdit = () => {
  editMode.value = false;
  previewImage.value = null;
  imageUrl.value = '';
  profileImage.value = null;
};

const handleDelete = (postID) => {
  posts.value = posts.value.filter(post => post.id !== postID);
}

</script>
