<template>
    <div class="p-4 bg-gray-900 border border-gray-700 rounded-lg flex justify-between items-center">
        <!-- sender image and display name-->
        <div class="flex items-center space-x-4">
            <img :src="sender.profileImage" alt="" class="rounded-full w-24 h-24">
            <p class="font-semibold text-2xl">
                {{ sender.displayName }}
            </p>
            <p class="text-gray-400 ">
                Host: {{ sender.host }}
            </p>
        </div>
        <!-- Buttons -->
        <div>
            <button @click="acceptRequest" class="py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-500 mr-2">
                Accept
            </button>
            <button @click="declineRequest" class="py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-500">
                Decline
            </button>
        </div>
    </div>
</template>

<script setup>
import { useAuthorStore } from '../../stores/user';
import api from '@/services/api';

    const props = defineProps({
            sender: Object,
        });

    const emit = defineEmits(['delete-item']);
    const authorStore = useAuthorStore();
    const encoded = encodeURIComponent(props.sender.id);

    const deleteRequest = () => {
        emit('delete-item');
    }

    const acceptRequest = async () => {
        try{
            const response = await api.put(
                `/api/authors/${authorStore.uid}/followers/${encoded}`,
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${authorStore.accessToken}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            if (response.status >= 200 && response.status < 300) {
                deleteRequest();
            }
        } catch (error) {
            console.log('Error accepting request', error);
        };
    }

    const declineRequest = async () => {
        try {
            const response = await api.post('/follow/request/reply/', {
                    actor: encoded,
                    object: authorStore.uid,
                    reply: false
                },
                {
                    headers: {
                        'Authorization': `Bearer ${authorStore.accessToken}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            if (response.status >= 200 && response.status < 300) {
                deleteRequest();
            }
        } catch (error) {
            console.log('Error declining request', error);
        }
    }
</script>