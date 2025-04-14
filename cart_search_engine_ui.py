import gradio as gr

from cart_search_engine import CartSearchEngine
from src.utils.ui_helper import category_icon


class CartSearchEngineUI(CartSearchEngine):
    def __init__(self):
        super().__init__()
        self.gradio_interface = None

    def launch_ui(self):
        with gr.Blocks() as demo:
            gr.Markdown("## 🛒 CART Search Engine UI")

            username_state = gr.State()
            login_section = gr.Column(visible=True)
            search_section = gr.Column(visible=False)

            with login_section:
                user_input = gr.Textbox(label="Enter your User ID")
                login_btn = gr.Button("Login")
                login_msg = gr.Textbox(visible=False, interactive=False, label="")

            with search_section:
                query_input = gr.Textbox(label="Enter your Search Query")
                search_btn = gr.Button("Search")
                # output_box = gr.Textbox(label="Top 5 Results", lines=10, interactive=False)
                results_html = gr.HTML()
                logout_btn = gr.Button("Logout", variant="stop")

            # Login logic
            def handle_login(user_id):
                if not self.verify_user(user_id):
                    return gr.update(visible=True), gr.update(visible=False), "❌ User not found", user_id
                self.create_session()
                self._initialize_search_components()
                return gr.update(visible=False), gr.update(visible=True), "", user_id

            login_btn.click(
                fn=handle_login,
                inputs=[user_input],
                outputs=[login_section, search_section, login_msg, username_state]
            )

            # Search logic
            def handle_search(query, user_id):
                if not user_id or not query:
                    return "<div style='color:red;'>⚠️ Please enter both User ID and Search Query.</div>"

                if not app.verify_user(user_id):
                    return "<div style='color:red;'>❌ Invalid User ID. Please try again.</div>"

                results = app._run_ui_search(query)

                if not results:
                    return "<div style='color:gray;'>😕 No results found.</div>"

                html = """
                <h3 style="margin-top: 10px; color:#4F46E5; font-size:18px;">🔎 Top Matches Found</h3>
                <div style='display:flex; flex-direction:column; gap:12px; padding-top:10px; font-family:Arial,sans-serif;'>
                """

                for i, title in enumerate(results[:5], 1):
                    icon = category_icon(title)
                    html += f"""
                    <div style="
                        background: #ffffff;
                        border-left: 5px solid #4F46E5;
                        border-radius: 10px;
                        padding: 14px 18px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                        transition: transform 0.2s ease;
                    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                        <div style="font-size: 15.5px;">
                            {icon} <strong>{i}. {title}</strong>
                        </div>
                    </div>
                    """

                html += "</div>"
                return html

            search_btn.click(
                fn=handle_search,
                inputs=[query_input, username_state],
                outputs=results_html
            )

            # Logout logic
            def handle_logout():
                self.terminate_session()
                self.current_user = None
                return gr.update(visible=True), gr.update(visible=False), "", ""

            logout_btn.click(
                fn=handle_logout,
                inputs=[],
                outputs=[login_section, search_section, login_msg, username_state]
            )

        demo.launch()

    def _display_and_log_results(self, query_log, bm25_results, vector_results, fused, product_mapping=None):
        """Display and log search results into query log"""
        bm25_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in bm25_results
        ]
        vector_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in vector_results
        ]
        final_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in fused
        ]

        # Update query log with titles
        query_log.update_results(bm25_products, vector_products, final_products)

        return final_products

    def _run_ui_search(self, query):
        """Main search pipeline executor"""
        ## 1. Query logging
        query_log = self._create_query_log(query)
        print(f"\nQuery log {query_log.id} added at {query_log.timestamp}")
        print(f"# Queries in Session: {len(self.current_session.queries)}")

        ## 2. Query pre-processing
        refined_query = self._preprocess_query(query_log, self.current_user)
        print(f"Refined search query: {query_log.refined_query}")

        ## 3. Embedding generation
        query_embedding = self._generate_query_embeddings(query_log)
        print(f"Query Vector: {query_log.embedding}")

        ## 4. Session context processing (Session + User)
        context_vector = self._build_session_context(alpha=self.context_alpha)
        print(f"Context Vector: {context_vector}")

        ## 5. Unified Context Embedding (context + query embeddings)
        unified_vector = self._generate_unified_embedding(query_embedding, context_vector,
                                                          alpha=self.context_fusion_beta)
        print(f"Unified Context Vector: {unified_vector}")

        ## 6. Dual retrieval
        bm25_results, vector_results = self._retrieve_results(refined_query, unified_vector)

        ## 7. Result fusion
        fused_results = self._fuse_search_results(bm25_results, vector_results, beta=self.retrieval_fusion_beta,
                                                  top_n=self.search_K)

        ## 8. Final logging
        products = self._display_and_log_results(query_log, bm25_results, vector_results, fused_results,
                                                 self.product_lookup)

        return products


if __name__ == "__main__":
    app = CartSearchEngineUI()
    app.launch_ui()
