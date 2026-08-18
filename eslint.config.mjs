import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([globalIgnores([
    "wagtailyoast/static/wagtailyoast/dist",
    "wagtailyoast/static/wagtailyoast/src/js/yoastworker.js",
    "**/build",
    "**/conf",
    "**/mediafiles",
    "**/node_modules",
    "**/tests",
])]);