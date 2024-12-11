<template>
    <main class="w-full bg-gray-900 min-h-screen">
        <div v-if="author" class="max-w-3xl mx-auto grid grid-cols-1 gap-6">
            <div class="flex justify-center items-center flex-col">
                <img :src="author.profileImage" class="rounded w-40 h-40 items-center">
                <p class="font-bold text-2xl">
                    {{ author.displayName }}
                </p>
                <div v-if="relation">
                    <button @click="sendUnfollow" v-if="relation === 'FOLLOWING' || relation === 'FRIENDS'"  class="py-2 px-4 bg-gray-900 text-white rounded-lg mr-2 opacity-75 border border-gray-600">Unfollow</button>
                    <button v-else-if="relation === 'PENDING'" disabled class="py-2 px-4 bg-purple-700 text-white rounded-lg mr-2 opacity-50">Pending</button>
                    <button @click="sendRequest" v-else class="py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-500 mr-2">Follow</button>
                </div>
                <p>
                Biography: {{ author.biography }}
                </p>
                <p>
                    github: {{ author.github }}
                </p>
                <p>
                    host: {{ author.host }}
                </p>
            </div>
            <h2 class="text-3xl font-bold border-b-2 border-gray-600 pb-2 text-center">Public Posts</h2>
            <div v-if="posts.length > 0">
                <PostCard v-for="post in posts" :key="post.id" :post="post" class="mt-5"/>
            </div>
            <div v-else>
                <p>Author has no public posts available.</p>
            </div>
        </div>
        <div v-else class="flex items-center justify-center min-h-screen">
            <Loader class="-ml-4"/>
        </div>
    </main>
</template>

<script setup>
import PostCard from '@/components/PostCard.vue';
import { useAuthorStore } from '../../stores/user';
import { ref, defineProps, onMounted } from 'vue';
import { follow } from '@/functions';
import api from '@/services/api';
import * as commonmark from 'commonmark';
import Loader from '@/components/Loader.vue';

// Initialize CommonMark parser and renderer
const reader = new commonmark.Parser();
const writer = new commonmark.HtmlRenderer();

const props = defineProps(['id']);
const authorStore = useAuthorStore();
const author = ref();
const relation = ref();
// Ref for storing posts data
const posts = ref([]);
const encoded = encodeURIComponent(props.id);
const uid = props.id.split('/').pop();

onMounted(async () => {
    // fetch the author's data
    try {
        console.log("fetching author data");
        const response = await api.get(`/api/authors/${encoded}/`, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        author.value = response.data;
    } catch (error) {
        console.log("Error fetching profile");
        throw error;
    }
    // if user is logged in and viewing the profile, fetch relation
    if (authorStore.isAuthenticated) {
        console.log("fetching follow relation");
        try {
            const response = await api.get(
                `/api/authors/${authorStore.uid}/followers/${encoded}`,
                {
                    headers: { 
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
            relation.value = response.data;
        } catch (error) {
            console.log("Did not find follow relation");
            relation.value = error.response.data;
        }
    }
    fetchPublicPosts();
});

// Function to render content in CommonMark format
const renderCommonMark = (content) => {
  const parsed = reader.parse(content);
  return writer.render(parsed);
};


// sends a post to the create follow request endpoint
const sendRequest = async () => {
    try {
        await follow(authorStore.uid, author.value);
        relation.value = 'PENDING';
    } catch (error) {
        console.log('Error sending follow request', error);
    }
};

// sends a post to unfollow
const sendUnfollow = async () => {
    try {
        const response = await api.delete(`/api/authors/${authorStore.uid}/followers/${encoded}`);
        if (response.status >= 200 && response.status < 300) {
            relation.value = 'NONE';
        }
    } catch (error) {
        console.log("Error unfollowing author");
        throw error;
    }
};

// Function to retrieve public posts for the author
const fetchPublicPosts = async () => {
    console.log("fetching posts");
  try {
    const response = await api.get(
        `/api/authors/${encoded}/posts/`,
        {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        }
    );
    posts.value = response.data['src'];
    console.log("posts", response.data);
  } catch (error) {
    console.error('Failed to load posts:', error);
  }
};
</script>