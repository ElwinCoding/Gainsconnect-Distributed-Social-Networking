<template>
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
        <Loader class="-ml-4"/>
    </div>
    <div v-else>
        <div class="flex flex-col space-y-10">
            <p v-if="senders.length === 0" class="font-bold text-center text-4xl">
                😓 No New Notifications 😓
            </p>
            <NotificationCard v-for="(sender, index) in senders" :key="sender.id" :sender="sender" @delete-item="deleteNotification(index)"/>
        </div>
    </div>

</template>

<script setup>
import NotificationCard from '@/components/NotificationCard.vue';
import axios from 'axios';
import { useAuthorStore } from '../../stores/user';
import { onMounted, ref } from 'vue';
import api from '@/services/api';
import Loader from '@/components/Loader.vue';

const authorStore = useAuthorStore();
const senders = ref([]);
const loading = ref(true);

    onMounted(async () => {
        try {
            const response = await api.get(`/follow/receive/${authorStore.uid}`);
            senders.value = response.data;
        } catch (error) {
            console.log("Failed getting requests", error);
        }
        loading.value = false;
    });

    const deleteNotification = (index) => {
        senders.value.splice(index, 1);
    };

</script>