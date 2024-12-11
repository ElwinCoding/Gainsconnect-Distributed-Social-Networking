<template>
  <main class="px-8 py-6 bg-gray-900 text-white min-h-screen">
    <div v-if="post === null">
    loading post...
    </div>
    <div v-else>
      <PostCard :post="post"/>
    </div>
  </main>
</template>

<script setup>
import PostCard from '@/components/PostCard.vue';
import axios from 'axios';
import { onMounted, ref } from 'vue';
import api from '../services/api';
import { useRoute } from 'vue-router'; // Import useRoute to access URL parameters
import { useAuthorStore } from '../../stores/user';

  const post = ref(null); // Reactive variable to store the post
  // const props = defineProps(['displayName', 'id']);

  // Use Vue Router to get route parameters
  const route = useRoute();
  const authorStore = useAuthorStore();

  onMounted(async () => {
    try {
      const authorUid = route.params.authorUid; // Extract authorUid from the URL
      const postUid = route.params.postUid; // Extract postUid from the URL

      const response = await api.get(`api/authors/${authorUid}/posts/${postUid}/`) //, {

      post.value = response.data; // Store the retrieved post in a reactive variable
    } catch (error) {
      console.error("Error fetching post", error);
    }
  });
</script>