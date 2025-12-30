<script>
    import { onMount } from 'svelte';
    import Connections from './Connections.svelte';
  
    let isValidPath = true;
  
    onMount(() => {
        const pathnameTrimmed = window.location.pathname.replace(/^\/+|\/+$/g, '');
        isValidPath = pathnameTrimmed === 'connections';
    });
</script>

{#if isValidPath}
    <Connections />
{:else}
    <div style="text-align: center; padding: 2rem; background-color: #121213; color: #ffffff; min-height: 100vh;">
        <h1>404</h1>
        <p>Page not found</p>
    </div>
{/if}
