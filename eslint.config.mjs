import { defineConfig } from "eslint/config";
import js from "@eslint/js";


export default defineConfig([
    {
        ignores: [
            "wagtailyoast/static/wagtailyoast/dist",
            "**/build",
            "**/conf",
            "**/mediafiles",
            "**/node_modules",
            "**/tests",
        ],
        files: ["wagtailyoast/static/wagtailyoast/src/**.js"],
        plugins: { js },
        extends: ["js/recommended"]
    }
]);