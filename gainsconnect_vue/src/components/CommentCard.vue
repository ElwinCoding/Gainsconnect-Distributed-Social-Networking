<template>
    <div class="bg-gray-700 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-white">
                {{ comment.author_name }}
            </span>
            <span class="text-sm text-gray-400">
                {{ formatDate(comment.created_at) }}
            </span>
        </div>
        <p class="text-gray-200">
            {{ comment.content }}
        </p>
    </div>
    
</template>

<script setup>
import { formatDate } from '@/functions';

    const props = defineProps({
        comment: Object
    });
</script>