import { defineStore } from "pinia";

export const useAuthorStore = defineStore('author', {
    state: () => ({
        isAuthenticated: false,
        id: null,
        uid: null,
        displayName: null,
        profileImage: null,
        biography: null,
        email: null,
        githubUser: null,
        accessToken: null,
        refreshToken: null,
        uid: null,
    }),
    actions: {
        logout() {
            this.isAuthenticated = false;
            this.id = null;
            this.displayName = null;
            this.profileImage = null;
            this.biography = null;
            this.email = null;
            this.githubUser = null;
            this.accessToken = null;
            this.refreshToken = null;
        },
        setInfo(data) {
            this.isAuthenticated = true;
            this.displayName = data['displayName'];
            this.profileImage = data['profileImage'];
            this.biography = data['biography'];
            this.email = data['email'];
            this.githubUser = data['github'];
            this.accessToken = data['access'];
            this.refreshToken = data['refresh'];
            this.id = data['id'];
            this.uid = data['id'].split('/').pop();
        },
        changeInfo(data) {
            this.displayName = data['displayName'];
            this.profileImage = data['profileImage'];
            this.biography = data['biography'];
            this.email = data['email'];
            this.githubUser = data['github'];
        }
    },
});
