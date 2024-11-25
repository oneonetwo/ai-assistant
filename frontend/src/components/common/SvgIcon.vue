<template>
    <svg class="svg-icon" :class="name">
    <use :href="`#icon-${name}`" />
    </svg>
    </template>
    <script setup lang="ts">
    defineProps<{
    name: string
    }>()
    </script>
    <style lang="scss">
    .svg-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
    vertical-align: middle;
    }
    </style>