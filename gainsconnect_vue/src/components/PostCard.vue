<template>
    <div class="p-6 bg-gray-800 border border-gray-700 rounded-lg">
        <!-- If post is original post -->
        <div class="mb-6 flex flex-col">
            <div class="mb-6 flex items-center justify-between">
                <!-- header -->
                <div class="flex items-center space-x-6">
                    <img :src="post.author.profileImage || '/default-profile.png'"
                        class="w-[50px] h-[50px] rounded-full">
                    <p>
                        <strong>{{ post.author.displayName }}</strong>
                        <span class="text-gray-400 text-xs">({{ post.visibility }})</span>
                    </p>
                </div>
                <!-- Date and ellipsis menu -->
                <div class="flex items-center space-x-2 relative">
                    <p class="text-gray-400">{{ formatDate(post.updated_at) }}</p>
                    <div v-if="authorStore.uid === getUidFromId(post.author.id)" class="relative">
                        <button @click="menuToggle = !menuToggle" class="text-gray-500 hover:text-gray-300 focus:outline-none">
                            &#x22EE;
                        </button>
                        <!-- Dropdown Menu -->
                        <div v-if="menuToggle"
                            class="absolute right-0 mt-1 w-28 bg-gray-700 border border-gray-600 rounded-md shadow-lg z-10">
                            <button @click="editPost"
                                class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left">
                                Edit
                            </button>
                            <button @click="deletePost"
                                class="block px-4 py-2 text-sm text-red-500 hover:bg-gray-600 w-full text-left">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Conditional rendering for edit mode -->
            <div v-if="postCopy.isEditing">
                <input v-model="postCopy.editableTitle" type="text"
                    class="p-2 w-full bg-gray-700 text-white rounded-lg mb-2" placeholder="Edit Title">
                <input v-model="postCopy.editableDescription" type="text"
                    class="p-2 w-full bg-gray-700 text-white rounded-lg mb-2" placeholder="Edit description">
                <textarea v-model="postCopy.editableContent" class="p-4 w-full bg-gray-700 text-white rounded-lg"
                    placeholder="Edit content"></textarea>
                <div class="flex items-center">
                    <label for="visibility" class="mr-2">Visibility:</label>
                    <select v-model="postCopy.editableVisibility" id="visibility"
                        class="bg-gray-600 text-white rounded-lg px-2 py-1">
                        <option value="PUBLIC">Public</option>
                        <option value="UNLISTED">Unlisted</option>
                        <option value="FRIENDS">Friends-Only</option>
                    </select>
                </div>
                <div class="flex items-center">
                    <label for="format" class="mr-2">Format:</label>
                    <select v-model="post.editableFormat" id="format"
                        class="bg-gray-600 text-white rounded-lg px-2 py-1">
                        <option value="standard">Standard</option>
                        <option value="commonmark">CommonMark</option>
                    </select>
                </div>
                <button @click="savePost"
                    class="inline-block mt-2 py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-800">
                    Save
                </button>
                <button @click="postCopy.isEditing = false"
                    class="inline-block mt-2 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-800">
                    Cancel
                </button>
            </div>

            <!-- Content -->
            <div>
                <RouterLink :to="{name: 'postDetail', params: { authorUid: getUidFromId(post.author.id), postUid: post.uid }}">
                    <h2 class="text-xl font-semibold text-white hover:underline">{{ postCopy.title }}</h2>
                </RouterLink>
                <p class="text-gray-300">{{ postCopy.description }}</p>
                <div v-if="postCopy.contentType === 'text/markdown'" v-html="renderCommonMark(post.content)"></div>
                <div v-else-if="postCopy.contentType === 'image/jpeg;base64' || postCopy.contentType === 'image/png;base64'" class="flex justify-center items-center">
                    <img :src="getImageSrc(postCopy.content, postCopy.contentType)" alt="Post Image" class="max-w-full h-auto rounded-lg"/>
                </div>
                <p v-else class="text-white mt-4">{{ postCopy.content }}</p>
                <p class="text-white mt-6">{{ postCopy.likes }} likes</p>
            </div>
        </div>
        <!-- Buttons -->
        <div class="flex justify-between">
            <button @click="toggleComments"
                class="inline-block mt-4 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-800 w-40">
                {{ commentToggle ? "Hide Comments" : "Show Comments" }}
            </button>
            <!-- <button @click="sharePost" v-if="post.visibility === 'PUBLIC'"
                class="inline-block mt-4 py-2 px-4 text-white rounded-lg bg-purple-600 hover:bg-purple-800">
                Share Post
            </button> -->
            <button @click="likePost"
                class="inline-block mt-4 py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-800">
                Like This Post
            </button>
        </div>
        <!-- Comments -->
        <div v-if="commentToggle" class="mt-6 border-t border-gray-700 pt-4">
            <!-- Comment input box -->
            <div class="bg-gray-700 rounded-lg p-4 mb-4">
                <textarea v-model="newComment" class="p-2 w-full bg-gray-600 text-white rounded-lg"
                    placeholder="Write a comment..." rows="2">
                </textarea>
                <button @click="addComment"
                    class="mt-2 py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-500">
                    Add Comment
                </button>
            </div>
            <!-- Comment list container -->
            <div class="space-y-4">
                <CommentCard v-for="comment in commentList" :key="comment.id" :comment="comment" />
            </div>
        </div>
    </div>
</template>

<script setup>
import CommentCard from './CommentCard.vue';
import { useAuthorStore } from '../../stores/user';
import { reactive, ref, defineEmits } from 'vue';
import * as commonmark from "commonmark";
import { useToast } from 'vue-toastification';
import { formatDate } from '@/functions';
import { onMounted } from 'vue';
import api from '../services/api'; //**TRY TO USE THIS INSTEAD OF AXIOS**

const menuToggle = ref(false);
const commentToggle = ref(false);
const commentList = ref([]);
const newComment = ref();

const authorStore = useAuthorStore();
const token = authorStore.accessToken;

const reader = new commonmark.Parser();
const writer = new commonmark.HtmlRenderer();

// Dynamically determine API URL
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const apiBaseUrl = isLocalhost
    ? 'http://127.0.0.1:8000'
    : 'https://gainsboro-f5f74d5f43ca.herokuapp.com';

const toast = useToast();
const emit = defineEmits();

const props = defineProps({
    post: Object
});

    // Utility function to extract UID from URL
    const getUidFromId = (id) => {
        if (!id) return null;
        const parts = id.split('/');
        return parts[parts.length - 1];
    };

    const postCopy = reactive({
        ...props.post,
        isEditing: false,
        likes: 0,
        content: props.post.content,
        contentType: props.post.contentType
    });

    const getImageSrc = (content, contentType) => {
        if (!content) return '';
        return content.startsWith('data:') 
            ? content 
            : `data:${contentType},${content}`;
    };


    const renderCommonMark = (content) => {
        const parsed = reader.parse(content);
        return writer.render(parsed);
    };

    const handleImageError = (e) => {
        // Fallback to default image or hide the image element
        e.target.style.display = 'none';
        console.error('Failed to load image:', e.target.src);
    };
    
    const toggleComments = async () => {
        commentToggle.value = !commentToggle.value;
        if (commentToggle.value && commentList.value.length === 0 ) {
            await fetchComments();
        }
    };

    const fetchComments = async () => {
        try {
            const response = await api.get(
                `/comment/${props.post.uid}/comments/`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    }
                }
            );
            console.log("comments", response.data);
            commentList.value = response.data;
            console.log("comments", response.data);
        } catch (error) {
            console.error("Error fetching comments", error);
        }
    };

const addComment = async () => {
    if (!newComment.value.trim()) return;

    try {
        const response = await api.post(`/comment/${props.post.uid}/comments/add/`,
            {
                content: newComment.value,
                post: props.post.uid,
                content_type: "application/json",
                
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        if (response.status >= 200 && response.status < 300) {
            newComment.value = "";
            commentList.value.unshift(response.data);
            console.log("Comment added successfully");
        }
    } catch (error) {
        console.error("Error adding comment", error);
    }
};

    const likePost = async () => {
        try {
            console.log("sending like");
            const postUrl = `${apiBaseUrl}/posts/${props.post.uid}/`; // Full URL as expected by the server
            console.log(apiBaseUrl);
            const response = await api.post(
                `${apiBaseUrl}/comment/${props.post.uid}/likes/add/`,
            {
                post: postUrl, // Pass the full post URL here
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            }
            );
            if (response.status >= 200 && response.status < 300) {
                postCopy.likes = Number(postCopy.likes || 0) + 1;;
                toast.success("Liked Post");
            }
        } catch (error) {
            console.error("Error liking post", error);
        }
    };

const sharePost = async () => {
    const confirmation = window.confirm("Do you want to share this post?");
    if (!confirmation) {
        return;
    }

    console.log()

    try {
        const response = await api.post(
          `${apiBaseUrl}/posts/repost/`,
          {
            original_post_id: props.post.uid
          },
          {
            headers: {
              "Authorization": `Bearer ${token}`,
              "Content-Type": "application/json"
            }
          }
        );
        if (response.status >= 200 && response.status < 300) {
            toast.success("Post Shared");
            emit('repost', response.data);
        }
    } catch (error) {
        console.error("Error reposting", error);
    }
};

const editPost = () => {
    postCopy.isEditing = true;
    postCopy.editableTitle = props.post.title;
    postCopy.editableContent = props.post.content;
    postCopy.editableDescription = props.post.description;
    postCopy.editableVisibility = props.post.visibility;
    postCopy.editableFormat = props.post.format;
};

    const deletePost = async() => {
        try {
            console.log("Deleting post");
            const response = await api.delete(`${apiBaseUrl}/api/posts/${props.post.uid}/delete/`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.status === 204) {
                console.log("Post deleted");
                emit('delete', props.post.uid);
            }
        } catch (error) {
            console.error("Error deleting post", error);
        }
    }

    const savePost = async() => {
        try {
            console.log("Saving edit...");
            const response = await api.put(
                `${apiBaseUrl}/api/posts/${props.post.uid}/edit/`,
                {
                    title: postCopy.editableTitle,
                    description: postCopy.editableDescription,
                    content: postCopy.editableContent,
                    visibility: postCopy.editableVisibility,
                    format: postCopy.editableFormat
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                }
            );
            if (response.status >= 200 && response.status < 300) {
                console.log("Saved edit on post");
                postCopy.isEditing = false;
                postCopy.title = postCopy.editableTitle;
                postCopy.description = postCopy.editableDescription;
                postCopy.content = postCopy.editableContent;
                postCopy.visibility = postCopy.editableVisibility;
                postCopy.format = postCopy.editableFormat;
            }
        } catch (error) {
            console.error("Error saving edit on post", error);
        }
    }

    const displayLikes = async () => {
        // const apiUrl = import.meta.env.VITE_API_URL;
        try {
            const response = await api.get(`/comment/${props.post.uid}/likes/count/`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
             
            postCopy.likes= Number(response.data.like_count|| 0);
            console.log( "LIKES" , response.data );
        } catch (error) {
            console.error("Error fetching like count", error);
        }
    }

// Fetch likes count when component mounts
onMounted(() => {
    displayLikes();
});

</script>