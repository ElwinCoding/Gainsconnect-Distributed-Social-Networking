<!--- Used in friends page -->
<template>
    <div class="p-4 bg-gray-800 border border-gray-700 rounded-lg flex items-center space-x-4">
        <img :src="user.profileImage" alt="" class="rounded-full w-24 h-24">
        <p class="font-semibold">{{ user.displayName }}</p>
        <p class="text-gray-400">Host: {{ user.host }}</p>
    </div>
</template>

<script setup>
const props = defineProps({
    user: Object
});

</script>