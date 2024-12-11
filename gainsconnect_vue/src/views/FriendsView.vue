<template>
    <div v-if="isLoading" class="flex items-center justify-center min-h-screen">
        <Loader class="-ml-4"/>
    </div>
    <div v-else class="grid grid-cols-3 gap-4 h-screen">
        <!-- Friends List -->
        <div class="flex-1 overflow-y-auto border border-gray-700 rounded-lg p-6 bg-gray-900">
            <h2 class="text-2xl font-semibold mb-4 text-center text-white">Friends</h2>
            <p v-if="friendsList.length === 0" class="font-bold text-center text-2xl">
                no friends 😭
            </p>
            <div class="space-y-4">
                <UserCard v-for="author in friendsList" :key="author.id" :user="author"/>
            </div>
        </div>
        <!-- Followers List -->
        <div class="flex-1 overflow-y-auto border border-gray-700 rounded-lg p-6 bg-gray-900">
            <h2 class="text-2xl font-semibold mb-4 text-center text-white">Followers</h2>
            <p v-if="followedList.length === 0" class="font-bold text-center text-2xl">
                no followers 😔
            </p>
            <div class="space-y-4">
                <UserCard v-for="author in followedList" :key="author.id" :user="author"/>
            </div>
        </div>
        <!-- Following List -->
        <div class="flex-1 overflow-y-auto border border-gray-700 rounded-lg p-6 bg-gray-900">
            <h2 class="text-2xl font-semibold mb-4 text-center text-white">Following</h2>
            <p v-if="followingList.length === 0" class="font-bold text-center text-2xl">
                no followings 😨
            </p>
            <div class="space-y-4">
                <UserCard v-for="author in followingList" :key="author.id" :user="author"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import axios from 'axios';
import { useAuthorStore } from '../../stores/user';
import { onMounted, ref } from 'vue';
import { getFollowingList } from '@/functions';
import UserCard from '@/components/UserCard.vue';
import api from '@/services/api';
import Loader from '@/components/Loader.vue';

    const authorStore = useAuthorStore();
    const followingList = ref([]);
    const followedList = ref([]);
    const friendsList = ref([]);
    const isLoading = ref(true);


    onMounted(async () => {
            try {
                const response = await getFollowingList(authorStore.uid);
                followingList.value = response;
                await getFollowedList();
                await getFriendsList();
                isLoading.value = false;
            } catch (error) {
                console.log("Failed getting requests");
                throw(error);
            }
        });

    const getFollowedList = async () => {
        try {
            const response = await api.get(`/api/authors/${authorStore.uid}/followers`);
            followedList.value = response.data.followers || [];
        } catch (error) {
            console.log("Error getting followed list");
            throw error;
        }
    }

    const getFriendsList = async () => {
        try {
            const response = await api.get(`/follow/list/${authorStore.uid}/friends`);
            console.log(response);
            friendsList.value = response.data;
        } catch (error) {
            console.log("Error getting friends list");
            throw error;
        }
    }
</script>