<template>
    <div class="flex justify-center items-start gap-0 min-h-screen">
        <Vue3Lottie :animationData="bicep" :height="250" :width="250" 
        />
        <p class="mt-40 mx-4 font-bold text-center text-6xl">
            Loading
        </p>
        <Vue3Lottie :animationData="bicep" :height="250" :width="250" 
        class="transform scale-x-[-1]"/>
    </div>
</template>


<script setup>
import { Vue3Lottie } from 'vue3-lottie';
import bicep from '@/assets/bicep.json';


</script>