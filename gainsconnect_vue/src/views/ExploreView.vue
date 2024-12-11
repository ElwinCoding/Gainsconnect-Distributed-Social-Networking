<template>
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
        <Loader class="-ml-4"/>
    </div>
    <div v-else>
        <p v-if="authors.length === 0" class="font-bold text-center text-2xl">
            😲No Other Authors on Node😲
        </p>
        <div class="grid grid-cols-4 gap-y-10 px-10">
            <div v-for="author in authors" :key="author.id" class="flex justify-center">
                <div class="w-[90%]">
                    <ExploreCard :author="author"/>
                </div>
            </div>
        </div>
    </div>
    
</template>

<script setup>
import ExploreCard from '@/components/ExploreCard.vue';
import axios from 'axios';
import { onMounted, ref } from 'vue';
import { useAuthorStore } from '../../stores/user';
import api from '@/services/api';
import Loader from '@/components/Loader.vue';

    const authors = ref([]);
    const authorStore = useAuthorStore();
    const loading = ref(true);

    // get all the authors on the server
    onMounted(async () => {
        try {
            const response = await api.get(`/follow/explore/${authorStore.uid}`);
            authors.value = response.data;
            loading.value = false;
        } catch (error) {
            console.error('Error fetching authors', error);
            throw error;
        }
    });
</script>