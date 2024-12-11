<template>
    <div class="bg-gray-900 border-gray-700 rounded-lg p-4 max-w-sm mx-auto">
        <!--- Profile -->
        <div class="flex flex-col items-center">
            <img :src="author.profileImage" alt="" class="w-24 h-24 rounded-full mb-2 object-cover">
            <p class="text-white text-lg font-bold">
                {{ author.displayName }}
            </p>
            <p class="text-gray-400">Host: {{ cleanedHost }}</p>
        </div>
        <!-- Buttons -->
        <div class="flex justify-center space-x-4 mt-4">
            <button v-if="author.relation == 'FOLLOWING' || author.relation == 'FRIENDS'" disabled class="py-2 px-4 bg-gray-900 text-white rounded-lg mr-2 opacity-50 border border-gray-600">Following</button>
            <button v-else-if="author.relation == 'PENDING'" disabled class="py-2 px-4 bg-purple-700 text-white rounded-lg mr-2 opacity-50">Pending</button>
            <button v-else @click="sendRequest" class="py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-500 mr-2">Follow</button>
            <RouterLink :to="{
                name: 'profile', 
                params: { id: author.id},
            }" class="py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-500">
                View
            </RouterLink>
        </div>
    </div>
</template>

<script setup>
import { follow } from '@/functions';
import { useAuthorStore } from '../../stores/user';

    const authorStore = useAuthorStore();

    const props = defineProps({
        author: Object
    });

    const cleanHost = (url) => {
        let host = url.split('/');
        host = host[2].split('-');
        if (host.length == 1) {
            return host[0];
        }
        if (host.length > 1) {
            host = host.slice(0, -1);
            host = host.join('-');
        }
        return host;
    }

    const cleanedHost = cleanHost(props.author.host);


    // sends a post to the create follow request endpoint
    const sendRequest = async () => {
        try {
            await follow(authorStore.uid, props.author);
            props.author.relation = 'PENDING';
        } catch (error) {
            console.log('Error sending follow request', error);
        }
    }
</script>