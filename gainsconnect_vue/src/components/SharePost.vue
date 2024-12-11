<template>
    <!-- If post is a repost -->
        <div v-if="post.original_post" class="mb-6 flex flex-col">
            <!-- repost header -->
            <div class="flex items-center justify-between">
                <RouterLink :to="{name: 'postDetail', params: { authorUid: getUidFromId(post.author.id), postUid: getUidFromId(post.id) }}">
                    <strong class="hover:underline">{{ post.author.displayName }} reposted</strong>
                    <span class="text-gray-400 text-xs">({{ post.visibility }})</span>
                </RouterLink>
                <div class="flex items-center space-x-2 relative">
                    <!-- Date -->
                    <p class="text-gray-400">
                        {{ formatDate(post.updated_at) }}
                    </p>
                    <!-- Ellipsis button menu -->
                    <div v-if="authorStore.uid === getUidFromId(post.author.id)" class="relative">
                        <button @click="menuToggle = !menuToggle" class="text-gray-500 hover:text-gray-300 focus:outline-none">
                            &#x22EE;
                        </button>
                        <!-- Dropdown menu -->
                        <div v-if="menuToggle"
                            class="absolute right-0 mt-1 w-28 bg-gray-700 border border-gray-600 rounded-md shadow-lg z-10">
                            <button @click="deletePost"
                                class="block px-4 py-2 text-sm text-red-500 hover:bg-gray-600 w-full text-left">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Original post -->
            <div v-if="post.original_post_data === 'deleted'"
                class="border border-gray-600 bg-gray-700 p-4 rounded-md mt-3">
                Original post was deleted
            </div>
            <div v-else class="border border-gray-600 bg-gray-700 p-4 rounded-md mt-3">
                <!-- header -->
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-6">
                        <img :src="post.original_post_data.author.profileImage || 'default-profile.png'" alt=""
                            class="w-[50px] h-[50px] rounded-full">
                        <p>
                            <strong>{{ post.original_post_data.author.displayName }}</strong>
                            <span class="text-gray-400 text-xs">({{ post.original_post_data.visibility }})</span>
                        </p>
                    </div>
                    <div>
                        <p class="text-gray-400">{{ formatDate(post.original_post_data.updated_at) }}</p>
                    </div>
                </div>
                <!-- Content -->
                <div class="mt-3">
                    <RouterLink :to="{name: 'postDetail', params: { authorUid: getUidFromId(post.original_post_data.author.id), postUid: post.original_post_data.uid }}">
                    <h2 class="text-xl font-semibold text-white hover:underline">{{ post.original_post_data.title }}</h2>
                    </RouterLink>
                    <p class="text-gray-300">{{ post.original_post_data.description }}</p>
                    <div v-if="post.original_post_data.content_type === 'text/markdown'"
                        v-html="renderCommonMark(post.original_post_data.content)"></div>
                    <p v-else class="text-white mt-4">{{ post.content }}</p>
                    <div v-if="post.original_post_data.image_data">
                        <img :src="post.original_post_data.image_data" alt="Post Image">
                    </div>
                </div>
            </div>
        </div>
</template>

<script setup>

</script>
