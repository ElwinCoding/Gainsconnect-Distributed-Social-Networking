<template>
    <div class="bg-gray-900 h-dvh w-64 border-r border-gray-800 py-10 px-7 sticky top-0 text-xl z-30">
        <div class="flex flex-col space-y-4">
            <!-- Logo -->
            <div class="flex items-center">
                <img :src="biceps" alt="GainsConnect Logo" class="w-10 h-10 rounded" />
                <span class="text-2xl font-bold">GainsConnect</span>
            </div>
            <!-- Profile Image -->
            <div class="flex flex-col items-center">
                <img :src=authorStore.profileImage alt="" class="rounded-full w-16 h-16">
                <p class="font-bold text-center mt-2">
                    {{ authorStore.displayName }}
                </p>                
            </div> 

            <!-- Menu -->
            <div class="border-t border-b border-gray-400 py-3 flex-col items-center space-y-4">
                <RouterLink to="/stream" class="w-full flex justify-left items-center space-x-4 hover:text-purple-400 hover:bg-gray-800 transition-colors duration-200 ease-in-out rounded">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
                    </svg>
                    <p>
                        Stream
                    </p>
                </RouterLink>

                <RouterLink to="/explore" class="w-full flex justify-left items-center space-x-4 hover:text-purple-400 hover:bg-gray-800 transition-colors duration-200 ease-in-out rounded">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m6.115 5.19.319 1.913A6 6 0 0 0 8.11 10.36L9.75 12l-.387.775c-.217.433-.132.956.21 1.298l1.348 1.348c.21.21.329.497.329.795v1.089c0 .426.24.815.622 1.006l.153.076c.433.217.956.132 1.298-.21l.723-.723a8.7 8.7 0 0 0 2.288-4.042 1.087 1.087 0 0 0-.358-1.099l-1.33-1.108c-.251-.21-.582-.299-.905-.245l-1.17.195a1.125 1.125 0 0 1-.98-.314l-.295-.295a1.125 1.125 0 0 1 0-1.591l.13-.132a1.125 1.125 0 0 1 1.3-.21l.603.302a.809.809 0 0 0 1.086-1.086L14.25 7.5l1.256-.837a4.5 4.5 0 0 0 1.528-1.732l.146-.292M6.115 5.19A9 9 0 1 0 17.18 4.64M6.115 5.19A8.965 8.965 0 0 1 12 3c1.929 0 3.716.607 5.18 1.64" />
                    </svg>
                    <p>
                        Explore
                    </p>
                </RouterLink>

                <RouterLink to="/friends" class="w-full flex justify-left items-center space-x-4 hover:text-purple-400 hover:bg-gray-800 transition-colors duration-200 ease-in-out rounded">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
                    </svg>
                    <p>
                        Friends
                    </p>
                </RouterLink>

                <RouterLink to="/notifications" class="w-full flex justify-left items-center space-x-4 hover:text-purple-400 hover:bg-gray-800 transition-colors duration-200 ease-in-out rounded">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"/>
                    </svg>
                    <p>
                        Notifications
                    </p>
                </RouterLink>
            </div>
            <div class="py-1 flex-col items-center space-y-4 mt-[-2]">
                <RouterLink :to="'/author/' + authorStore.displayName" class="w-full flex justify-left items-center space-x-4 hover:text-purple-400 hover:bg-gray-800 transition-colors duration-200 ease-in-out rounded">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/>
                    </svg>
                    <p>
                        Profile
                    </p>
                </RouterLink>
                <button @click="logout" class="w-full flex justify-left items-center space-x-4 hover:bg-red-700 transition-colors duration-200 ease-in-out rounded">
                    <svg  viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-white">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M15.9908 7.82251C16.2897 7.5357 16.7644 7.54547 17.0512 7.84433L20.541 11.4807C20.8195 11.7709 20.8195 12.2291 20.541 12.5193L17.0512 16.1557C16.7644 16.4545 16.2897 16.4643 15.9908 16.1775C15.692 15.8907 15.6822 15.4159 15.969 15.1171L18.2404 12.7502L11.2727 12.7502C10.8585 12.7502 10.5227 12.4144 10.5227 12.0002C10.5227 11.586 10.8585 11.2502 11.2727 11.2502L18.2408 11.2502L15.969 8.88295C15.6822 8.58409 15.692 8.10932 15.9908 7.82251Z" fill="currentcolor"/>
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M3.25 4C3.25 3.58579 3.58579 3.25 4 3.25H13.4545C13.8688 3.25 14.2045 3.58579 14.2045 4V7C14.2045 7.41421 13.8688 7.75 13.4545 7.75C13.0403 7.75 12.7045 7.41421 12.7045 7V4.75H4.75V19.25H12.7045V17C12.7045 16.5858 13.0403 16.25 13.4545 16.25C13.8688 16.25 14.2045 16.5858 14.2045 17V20C14.2045 20.4142 13.8688 20.75 13.4545 20.75H4C3.58579 20.75 3.25 20.4142 3.25 20V4Z" fill="currentcolor"/>
                    </svg>
                    <span class="ml-2">Logout</span>
                </button>
            </div>
        </div>

        <!-- Logout confirmation -->
        <div v-if="showLogoutModal" class="fixed inset-0 bg-black bg-opacity-50">
        </div>
        <div v-if="showLogoutModal" class="fixed inset-0 flex items-center justify-center">
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl">
                <h3 class="text-xl font-bold mb-4">Confirm Logout</h3>
                <p class="mb-6">Are you sure you want to log out?</p>
                <div class="flex justify-end space-x-4">
                    <button 
                        @click="showLogoutModal = false"
                        class="px-4 py-2 bg-gray-600 rounded hover:bg-gray-700 transition-colors"
                    >
                        Cancel
                    </button>
                    <button 
                        @click="confirmLogout"
                        class="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition-colors"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue';
    import { RouterLink, useRouter } from 'vue-router';
    import axios from 'axios';
    import { useAuthorStore } from '../../stores/user';

    const router = useRouter();
    const authorStore = useAuthorStore();
    const biceps = import.meta.env.PROD ? '/static/images/biceps.png' : '/images/biceps.png';
    const showLogoutModal = ref(false);

    // shows the logout confirmation
    const logout = () => {
        showLogoutModal.value = true;
    };

    // clears the local storage, authorStore and redirects to login page
    const confirmLogout = () => {
        localStorage.clear();
        axios.defaults.headers.common['Authorization'] = null;
        authorStore.logout();
        showLogoutModal.value = false;
        router.push('/login');
    };
</script>