<template>
  <main class="px-8 py-6 bg-gray-900 text-white min-h-screen">
    <div class="max-w-3xl mx-auto grid grid-cols-1 gap-6">
      <h1 class="text-3xl font-bold mb-6 text-center">Personal Feed</h1>
      <!-- Post input box -->
      <PostForm/>
      <div class="flex flex-col justify-center space-y-6">
        <!-- Display posts if exist -->
        <div v-if="posts.length > 0">
          <PostCard v-for="post in posts" :key="post.uid" :post="post" @delete="handleDelete" @repost="handleRepost" class="mt-5"/>
        </div>

        <!-- No posts available -->
        <div v-else>
          <p class="text-center text-gray-400">No posts available.</p>
        </div>
      </div>

      <!-- GitHub Activity Section -->
      <div>
        <h2 class="text-2xl font-bold mb-6 text-center text-white">
          GitHub Activity
        </h2>
        <div v-if="githubEvents.length">
          <div
            v-for="event in githubEvents"
            :key="event.id"
            class="p-6 bg-gray-800 border border-gray-700 rounded-lg mb-4"
          >
            <div class="flex items-center justify-between">
              <p class="text-white font-semibold">{{ event.actor.login }}</p>
              <p class="text-gray-400">
                {{ new Date(event.created_at).toLocaleString() }}
              </p>
            </div>
            <p class="text-gray-400">{{ event.type }}</p>
            <p class="text-gray-300">{{ event.repo.name }}</p>
          </div>
        </div>
        <div v-else>
          <p class="text-center text-gray-400">
            No recent GitHub activity found.
          </p>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import PostForm from "@/components/PostForm.vue";
import { ref, provide, onMounted } from "vue";
import axios from "axios";
import { useAuthorStore } from "../../stores/user";
import { fetchPublicGitHubEvents } from "../services/githubService"; // Import your GitHub fetch function
import { refreshToken } from "@/functions";
import PostCard from "@/components/PostCard.vue";
import api from '../services/api';

export default {
  components: {
    PostForm,
    PostCard,
  },
  methods: {
    // Add this method
    getFullImageUrl(image) {
      return `http://localhost:8000${image}`;
    },
  },
  setup() {
    const posts = ref([]); // Holds the fetched posts
    provide('posts', posts);
    
    const githubEvents = ref([]); // Holds GitHub events
    const lastEventTime = ref("2024-08-01T00:00:00Z"); // Set the initial last event timestamp
    const authorStore = useAuthorStore(); // Access the store for authentication
    const usernames = ref([]); // Holds GitHub usernames
    const authorUid = authorStore.uid
      
      // Fetch posts from the API
      const fetchPosts = async () => {
        try {
          const token = authorStore.accessToken; // Get access token from the store
          const response = await api.get('/api/stream/', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (response.status === 200) {
          posts.value = response.data;
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          await refreshToken(authorStore);
          await fetchPosts();
        } else {
          console.error("Error fetching posts:", error);
        }
      }
    };

    // Fetch usernames from the backend
    const fetchUsernames = async () => {
      try {
        const response = await api.get(
          "/authors/github_usernames/"
        );
        usernames.value = response.data.usernames; // Store fetched usernames
        await getAllGitHubEvents(); // Fetch GitHub events for all usernames
      } catch (error) {
        console.error("Error fetching GitHub usernames:", error);
      }
    };

    // Fetch GitHub events for all usernames
    const getAllGitHubEvents = async () => {
      if (authorStore.githubUser != null && authorStore.githubUser !== "") {
        console.log("fetching github events for", authorStore.githubUser);
        try {
          const eventPromises = usernames.value
            .filter((username) => username !== null) // Filter out null usernames
            .map(async (username) => {
              const newEvents = await fetchPublicGitHubEvents(
                username,
                lastEventTime.value
              );
              return newEvents; // Return the events for each username
            });

          const eventsArray = await Promise.all(eventPromises); // Wait for all events to be fetched
          // Flatten the array and sort events by created_at from newest to oldest
          githubEvents.value = eventsArray.flat().sort((a, b) => {
            return new Date(b.created_at) - new Date(a.created_at);
          });

          if (githubEvents.value.length === 0) {
            console.log("No new events found for any user.");
          }
        } catch (error) {
          console.error("Error fetching GitHub events:", error);
        }
      }
      else {
        console.log("no github username user found");
      }
    };

    const handleDelete = (postUID) => {
      posts.value = posts.value.filter(post => post.uid !== postUID);
    }

    const handleRepost = (post) => {
      console.log("respoting");
      console.log("post", post);
      posts.value.unshift(post);
    }

    onMounted(() => {
      fetchPosts(); // Fetch posts when the component mounts
      fetchUsernames(); // Fetch GitHub usernames when the component mounts
    });

    return {
      handleRepost,
      handleDelete,
      posts,
      fetchPosts,
      authorUid,
      githubEvents,    
    };
  },
};
</script>
