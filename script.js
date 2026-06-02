document.addEventListener('DOMContentLoaded', () => {
    console.log('[AgentHub] Frontend environment initialized.');
    mountApp();
});

function mountApp() {
    const app = document.getElementById('app');
    if (!app) return;

    // 初始状态渲染
    app.innerHTML = `
        <header>
            <h1>AgentHub 控制台</h1>
        </header>
        <section id="content" class="mt-4">
            <p>静态资源加载完成，前端交互模块已就绪。</p>
        </section>
    `;

    // 预留状态管理与事件绑定入口
    window.__APP_STATE__ = { isReady: true, modules: [] };
}