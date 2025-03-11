# Context-aware-Search-Engine-for-E-commerce
Search engine for e-commerce product search that better captures user intent.


### 1. Literature Review

Information Retrieval (IR) aims to retrieve relevant documents for a user's query. Traditional IR models—Boolean retrieval, Vector Space Models (VSM) and probabilistic functions like BM25—assume that document relevance is fixed, independent of the user or search context. They primarily rely on keyword matching and statistical weighting, ignoring how user intent, behaviour, and situational factors affect relevance.

Conversely, **contextual IR** adapts to the dynamic nature of user searches. Users refine their queries and expect personalised results based on their past interactions. By integrating user behavior, search history, and semantic relationships, contextual IR delivers more accurate results, which is essential for e-commerce, conversational search, and recommendation systems.

Early IR models treated queries as independent and document relevance as universal. As these models struggled with ambiguous, evolving, or personalised searches, researchers developed context-aware retrieval methods that leverage structured knowledge, session history, and adaptive ranking. These advancements have paved the way for modern deep learning-based retrieval systems that adjust dynamically to user intent.

This review focuses on the transition from traditional IR models to modern context-aware systems, aiming to:

- Contrast traditional IR models with context-aware approaches.
- Discuss formal and data-driven methods for modelling context.
- Evaluate metrics and methodologies for contextual IR performance.
- Explore applications of contextual IR in e-commerce product search.
- Identify emerging trends and challenges in deploying context-aware IR systems.

We synthesises key research across personalised search, conversational search, query rewriting, multimodal IR, and neural retrieval techniques, with a focus on enhancing e-commerce search through improved understanding of user intent and session-based retrieval.

**1.1. Theoretical Foundations**. Melucci (2005) highlights the limitations of classical information retrieval (IR) models, pointing out that they do not adequately address the dynamic nature of user search needs. In contrast, contextual models adapt relevance based on factors such as time, location, and user-specific information. For example, Tourani et al. (2023) illustrate this shift with Point-of-Interest recommendation systems that adjust results based on the user's current context. Similarly, Wan et al. (2023) demonstrate that integrating context into retrieval systems significantly enhances answer accuracy compared to traditional conversational methods. Furthermore, Mohankumar et al. (2024) note that classical methods often struggle with short, ambiguous queries, particularly in sponsored search scenarios.

To capture the dynamic nature of relevance, formal context modelling in IR utilizes mathematical frameworks and logical formulations. Melucci (2005) introduces a framework that employs linear transformations within Vector Space Models to represent context shifts, allowing vector representations to evolve as document-query relationships change over time. Merrouni et al. (2019) provide a comprehensive survey of the evolution of contextual IR, critically analyzing the limitations of context-free systems and tracing the development of more robust context models over the past two decades, despite the absence of a precise definition for context. Building on these foundations, Mohankumar et al. (2024) propose a Fusion-in-Decoder architecture that integrates dense retrieval with non-autoregressive generation, representing context as an additional layer over traditional query representations.

Recent advancements in machine learning have further enhanced IR systems by incorporating contextual awareness and dynamic user modelling. Singh and Boursier (2024) introduce the Contextually Aware Personalised Information Retrieval (CAPIR) system, which utilizes evolutionary machine learning to continuously update user profiles and optimize retrieval strategies in real time. CAPIR combines a Term Vector Model for basic term matching with a Feature Vector Model that incorporates user-specific factors, such as historical behaviour and temporal relevance. Likewise, Zuo et al. (2022) present an end-to-end neural model for query rewriting in e-commerce search that employs graph-based attention mechanisms to capture relationships between queries, thereby refining and disambiguating search intent without requiring manual feature engineering. Additionally, Mohankumar et al. (2024) enhance query representations by integrating contextual signals from web search data and GPT-4-generated query profiles, resulting in richer embeddings that more accurately reflect the evolving nature of user queries. Collectively, these developments highlight a clear trend toward more nuanced and adaptive ML representations in modern information retrieval.

**1.2. Evaluation Frameworks.** Evaluation of contextual IR systems can be approached from multiple perspectives. System-centred evaluations adapt traditional Cranfield-style experiments to contextual IR. Tamine and Daoud (2018) describe static evaluation tracks—such as TREC Contextual Suggestion and TREC Microblog—that rely on simulated or predefined contexts with expert relevance judgments. Mohankumar et al. (2024) extend this by introducing a unified model, Augmented Unity, which integrates contextual signals specifically for sponsored search, enabling rigorous quantitative analysis.

User-centred evaluations, on the other hand, emphasise real user interactions through controlled lab studies and diary studies. Tamine and Daoud (2018) stress the importance of capturing multidimensional relevance, where dynamic contexts emerge from query reformulations and user feedback. This approach helps ensure that the system meets the nuanced needs of real users.

Hybrid evaluation frameworks combine quantitative metrics with qualitative assessments to offer a comprehensive view. For instance, Tamine and Daoud (2018) advocate using traditional metrics like MAP, nDCG, Time-Biased Gain, and ELG alongside qualitative measures such as user feedback and diary logs. Similarly, Singh and Boursier (2024) employ both quantitative metrics (precision, recall, MAP) and qualitative user feedback to validate the system's enhanced adaptability and user-centric design. Mohankumar et al. (2024) also combine offline metrics (e.g., precision, recall, GPU cost) with online measures (such as ad clicks and revenue uplift) to fully assess the effectiveness of their context-aware retrieval method.

**1.3. Some Applications in Contextual IR**. Contextual IR has found applications across several domains, notably in personalised recommendations, e-commerce search and sponsored search retrieval. In personalised recommendations, Tourani et al. (2023) introduced CAPRI—a Context-Aware Interpretable Point-of-Interest Recommendation Framework—that addresses limitations in conventional recommendation systems by incorporating dynamic user context. CAPRI leverages models such as GeoSoCa, LORE, and USG to improve recommendation accuracy, beyond-accuracy measures, and fairness, particularly for point-of-interest suggestions.

In the realm of e-commerce, Zuo et al. (2022) analyse query rewriting techniques that exploit session-based search histories. Their work demonstrates how multiple, related queries within a session can be used to infer a user’s true shopping intent, resulting in more precise query reformulations and, consequently, better product retrieval.

Meanwhile, context-aware passage retrieval has emerged as a critical area in document-grounded conversational systems. Hui Wan et al. (2024) explore methods to integrate personalised context from external knowledge bases, proposing personalised context-aware search (PCAS) to reduce factual hallucinations common in large language models such as ChatGPT, BARD, and BlenderBot.

Finally, in sponsored search retrieval, Mohankumar et al. (2024) show that augmenting ambiguous queries with contextual signals—derived from web search titles, snippets, and GPT-4–generated query rewrites—can significantly enhance ad-matching precision. Their Augmented Unity model demonstrates that enriching queries in this manner leads to better disambiguation of user intent, higher engagement, and increased ad revenue without extra serving costs.

**1.4. Comparative Analysis, Emerging Trends and Implications**. Formal methods (Melucci, 2005; Merrouni et al., 2019) use mathematical frameworks, like linear transformations in vector spaces, to model context with structured metadata. While they are interpretable, they often struggle with scalability in dynamic environments. On the other hand, deep learning methods derive context from user behaviour and embeddings, offering flexibility but requiring larger datasets and sacrificing interpretability.

Integration techniques vary: Tourani et al. (2023) apply fusion rules (product, sum, or sum-of-products) to combine contextual signals, while Wan et al. (2024) focus on concatenating or selectively integrating context to minimise noise.

Recent trends show an increasing use of advanced AI for adapting retrieval systems. Mohankumar et al. (2024) highlight how large language models like GPT-4 can improve query rewrites and explain intents, enhancing query clarity and retrieval accuracy. Meanwhile, Tamine and Daoud (2018) emphasise the importance of integrating long-term interaction data and real-time feedback for evolving user contexts while balancing performance and system constraints. However, challenges such as limited data, processing delays and privacy issues remain, particularly with short, ambiguous queries in resource-constrained transformer models.

This shift from static models like VSM and BM25 to adaptive, context-aware systems informs our project to create a context-aware search engine for e-commerce product search. We aim to develop a practical, scalable, and ethical retrieval system that leverages modern advancements in contextual information retrieval.

---

### 2. Proposed Methodology

**2.1. Aim, Task, Dataset**. In this project, we design and evaluate a context-aware search engine for e-commerce product search that better captures user intent. Traditional search engines often return irrelevant results due to short, ambiguous or incomplete queries.

**2.1.1. Search Task Definition**. Our search engine tackles two primary tasks:

(i) **Query Rewriting for Enhanced Intent Understanding**. E-commerce queries are often vague or misspelt (e.g., "iPhone case" vs. "iPhone 11 pro case sailor moon"). We rewrite ambiguous or incomplete queries by leveraging session history and contextual cues to infer user intent. This approach is inspired by graph-based query rewriting techniques (Zuo et al., 2022), which use session graphs and attention mechanisms to refine queries.

(ii) **Contextualized Ranking for Improved Product Retrieval**. Rather than treating each query in isolation, we incorporate user search history and semantic similarity to rank results more effectively. Drawing on Melucci (2005), our model employs vector space transformations to capture query context, enhancing precision and recall in product search.

**2.1.2. Datasets**. We evaluate our system using two real-world e-commerce datasets:

(i) **CHIIR21 Natural Language Queries Dataset**: Contains 3,560 user product needs in natural language, covering domains such as laptops and jackets. This dataset tests our system’s handling of verbose, natural queries.

(ii) **Shopping Queries Dataset**: Provides 40 candidate results per query with ESCI relevance judgments (Exact, Substitute, Complement, Irrelevant). This dataset is ideal for assessing ranking performance under varying query specificity.

These datasets offer a mix of short, ambiguous queries and detailed natural language queries, enabling comprehensive evaluation of our context-aware search engine in terms of retrieval effectiveness and ranking quality.

**2.2. Evaluation Plan**. We will evaluate our approach by comparing BM25 with context modelling and BM25 with query expansion (using a Transformer re-ranker) against baselines without these enhancements.

(i) **Accuracy metrics**.

- **Precision@k:** Proportion of relevant items in the top-k recommendations.
- **Recall@k:** Ability to retrieve all relevant items.
- **mAP@k:** Average precision across queries.

(i) **Fairness metrics** ensure that our system improves both the accuracy and fairness of product recommendations (Deldjoo et al., 2021; Rahmani et al., 2022; Wang et al., 2023).

- **MADr (Mean Absolute Deviation for Recommendations):** Measures disparities in performance across user groups, with lower values indicating more balanced recommendations.
- **GCE (Group Conditional Entropy):** Assesses diversity in recommendations within user groups; higher values indicate more diverse content exposure.

**2.3. Search Engine Architecture**. In many e-commerce environments, users usually perform multiple, sequential queries across a single session (e.g., “mechanical keyboard,” “gaming headphones,” “gaming laptop,” etc.). Traditional one-shot search engines tend to overlook important contextual signals from these queries.

We propose a context-aware search engine framework, **CART** (**C**ontext-**A**ware **R**etrieval **T**ransformer). This proposed architecture integrates short-term session-based signals and long-term user preferences to enhance retrieval relevance.

**2.3.1. Retrieval Models**. The system employs a two-stage pipeline:

(i) **Hybrid retrieval** using a **BM25 retrieval** model for fast, *lexical matching* and a **vector retrieva**l model for *semantic matching*. For short queries, BM25 often excels at precision for direct keyword matches, which is valuable for when users explicitly mentions certain brands or product attributes. Meanwhile, neural embeddings can capture synonyms, paraphrases and conceptual relations that lexical matching might miss (e.g., “headphones” and “earphones” might be close semantically).

- **BM25 Retrieval.** Takes in a preprocessed query as input, and retrieves top $K_\text{BM25}$ documents based on **term frequency** (TF)**, inverse document frequency** (IDF) and **length normalisation**. TF adjusts the raw frequency of terms to avoid overemphasising those that appear very frequently, while IDF assesses the rarity or significance of a term within the entire corpus. The BM25 score is calculated by multiplying the TF and IDF values for each query term and then summing these scores across all terms.\
    
    $$\text{BM25}(d, q) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{\text{TF}(t, d) \cdot (k_1 + 1)}{\text{TF}(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$
    
    For example, for the expanded query “headphones gaming Sony,” the initial BM25 candidate product list may look like: `[{id: 1, title: "Sony Gaming Headphones...", bm25_score: 12.3}, ...]`.
    
- **Vector Retrieval.** Retrieves top  $K_\text{VR}$ documents based on semantic alignment scoring (via cosine similarity) between a **unified query vector** $\mathbf{u}$ (preprocessed query embedding + user context vector) and each **product document embedding  $\mathbf{d}_D$**:\
    
    $$\text{Sim}(D, q_{\text{exp}}) = \cos(\mathbf{u}, \mathbf{d}_D) = \frac{\mathbf{u} \cdot \mathbf{d}_D}{\|\mathbf{u}\| \cdot \|\mathbf{d}_D\|}$$
    

The candidate sets from both retrievals are merged by either a **rank fusion** (e.g., reciprocal rank fusion) or a **score fusion** technique (e.g., a weighted sum of BM25 scores and vector similarity). Since BM25 and vector similarity scores may exist on different scales, they will be normalised (**min-max normalisation** or **Z-score) standardisation** before merging.\

$$\text{FinalScore}(D) = \beta \cdot \text{BM25}(D) + (1-\beta) \cdot \text{Sim}(D, q_{\text{exp}})$$

where β can be fine-tuned to balance lexical vs. semantic emphasis.

(ii) **Transformer re-ranker** for producing a estimating the final relevance of each candidate to the user’s query and context. We first prepare the input:

- **Refined Query Text**: Tokenise the expanded query using a pre-trained tokeniser (e.g.  "headphones" → Expanded to "gaming headphones Sony").
- **Unified Contextual Embedding**: Using the fused vector (e.g., $\bold{u}=\text{QueryEmbedding("gaming headphones Sony")}+\text{ContextVector("gaming":0.8, "Sony":0.6)}$). To ensure both embeddings occupy the same vector space, we use a project layer (e.g., linear transformation) their spaces. L2-normalisation is also applied to ensure that the context vector does not dominate our query embedding.
- **Candidate Documents**: Tokenise document titles/descriptions from the merged BM25 (e.g. “Sony  WH-1000XM5”) + Vector Retrieval candidate list (e.g., "Bose QC45").

We use a cross-encoder Transformer (e.g., BERT) fine-tuned for ranking. For each candidate item $d$, we get $\text{score}(q,d)$ from the cross-encoder, which will be then be re-sorted to obtain the final top K products ranking.

**2.3.2. SE Components**. The hybrid retrieval model is supported by the two core components:

(i). **LLM-based query preprocessor**. We refine raw queries using spelling correction and inject contextual terms from session history and user preference. Given an input query $q$, we use a pre-trained LLM to correct typos and obtain the cleaned query $q'$. From the search session graph, we obtain session terms $\mathcal{T}_s$ and user preferences $\mathcal{P}_u$*—*hence, our expanded query can be defined as $q_{\text{exp}} = q' \cup \left\{ t \, | \, t \in \mathcal{T}_s \cup \mathcal{P}_u \right\}$.

(ii). **Dynamic context modelling**. Comprises of two models: a session graph and a user profile

- **Session Graph**. ****Inspired by Zuo et al. (2023), the session graph is used to model short-term intent transitions by tracking intra-session behaviour. We further use this to infer long-term preferences for the User Profile model.
    
    Let $G_u​=(V_u​,E_u​)$  represent the session graph for user $u$, where $V_u=\{v_1,v_2,...\}$ are the nodes (queries or products) and $E_u=\{e_{ij}\}$ are the edges (transitions between nodes). Edge weights $w_{ij}$ reflect both frequency and recency of transitions, represented by the equation:
    
    $$
    w_{ij} = \frac{\text{count}(i \to j)}{\sum_{k} \text{count}(i \to k)}  
    $$
    
    where $\text{count}(i \to k)$ represents the number of times the user transitions from $i$, and the denominator normalises weights to sum to 1 for all edges leaving $i.$ For example, if a user transitions $\text{"laptop"}\to\text{"mouse"}$ 5 times and $\text{"laptop"}\to\text{"keyboard"}$ 3 times, then $w_{\text{laptop}\to\text{mouse}} = \frac{5}{8}$ and $w_{\text{laptop}\to\text{keyboard}} = \frac{3}{8}$.
    
    **Recency Adjustment**. To prioritise recent interactions, we apply weights decay exponentially over time:
    
    $$
    w_{ij}^{\text{recency}} = w_{ij} \cdot e^{-\lambda \Delta t}
    $$
    
    where $\Delta t$ is the time since last transition $i\to j$ and $\lambda$ controls decay rate.
    
- **User Profile**. Persistent user interests across sessions are captured by aggregating term weights using exponential time decay to downweigh older interactions. For example, for a term $t$ (e.g. “gaming”), its long-term preference weight $w_t$ is calculated as:
    
    $$
    w_t = \sum_{s \in \mathcal{S}_u} \mathbb{I}(t \in s) \cdot e^{-\lambda \Delta t_s},  
    $$
    

(iii). **Unified context vectorisation**. To retrieve a unified embedding $\mathbf{u}$, we combine the refined query text $q_{exp}$ with the context vector $\mathbf{c}_u$ (derived from the session graph and user profile). $\mathbf{c}_u$ is generated via term-weighted averaging (Melucci et al., 2005) and then combined with the query embedding via the sum rule (Tourani et al., 2023). To ensure $\mathbf{q}_{\text{exp}}$ and $\mathbf{c}_u$ occupy the same vector space, we also apply a linear transformation function to align their spaces.

$$
\mathbf{u} = \mathbf{q}_{\text{exp}} + \mathbf{W} \cdot \mathbf{c}_u
$$

where $\mathbf{W}$ is a learnable weight matrix.

![**Fig 1.** Overview of Search Engine Architecture](attachment:a4b99270-369a-4944-832d-697756893a26:FINAL_SA_IR.jpg)

**Fig 1.** Overview of Search Engine Architecture

![**Fig 2.** Sample Search User Interface](attachment:7c7a3f2b-0211-4443-9ce9-9dd9956c6762:e87c8a05-a5ff-4343-a237-20b8ac2cacdb.png)

**Fig 2.** Sample Search User Interface

**2.4. Development Tools**

- **GitHub**: Manages version control and code collaboration.
- **PyTorch**: For retraining models, fine-tuning deep learning architectures and implementing ML algorithms.
- **Microsoft Teams**: Facilitates communication, project management and deliverable coordination.
- **Python**: Primary programming language for development, supporting data preprocessing, model implementation and evaluation.

---

### 3. Project Plan

**3.1. Teamwork (Responsibilities)**.

| Scope  | Deliverable  | Assigned  | Details  |
| --- | --- | --- | --- |
| A1, A2  | Project Management  | Viriya, Mohammed  | **Viriya**: Scrum Board, Report Coordinator. 
**Mohammed**: Meeting Notes, GitHub Maintenance.  |
| A1  | Literature Review  | Everyone  | At least 5 papers each for brainstorming; 2 papers each for final written review.  |
| A1  | Aim, Task, Dataset  | Mohammed, Seyedeh  | **Mohammed**: Dataset, Evaluation Plan. 
**Seyedeh**: Problem Setup/Search Task.  |
| A1  | General Architecture of Search Engine  | Dania, Viriya  | -  |
| A1  | Description of Retrieval Model(s)  | Seyedeh  | -  |
| A1  | Development Tool(s)  | Mohammed  | -  |
| A1  | Teamwork & Time Plan  | Dania, Viriya  | **Viriya**: Teamwork
**Dania**: Time plan for search engine development.  |
| A2  | Source Code  | Everyone  | Classical IR model for benchmark (e.g. TF-IDF); Our proposed model  |
| A2  | Presentation Slides & Videos  | Everyone  | -  |

**3.2. Development Timeline**.

| Week  | Title  | Description  |
| --- | --- | --- |
| Week 1 (Mar 4 – Mar 10)  | Planning & Setup  | - **Finalise Requirements & Architecture**: Confirm features and design for the LLM-based Query Preprocessor. 
- **Environment Setup**: Configure development environments and prepare benchmark datasets.  |
| Week 2 (Mar 11 – Mar 17)  | Core Development Phase I  | - **LLM-Based Query Preprocessor**: Implement query rewriting with context injection. 
- **BM25 Retrieval Module**: Develop the lexical matching component.  |
| Week 3 (Mar 18 – Mar 24)  | Core Development Phase II   | - **Vector Retrieval Module**: Develop the semantic search component. 
- **Integration**: integrate BM25 and vector retrieval.  |
| Week 4 (Mar 25 – Mar 31)  | Integration & Tuning Phase I   | - **Score Fusion**: fuse outputs of BM25 and vector. 
- **Transformer Re-Ranker**:  integrate the re-ranker for fine-tuning the Top k results.  |
| Week 5 (Apr 1 – Apr 7)  | Optimisation & Finalisation | - **Optimisation**: Fine-tune score fusion and re-ranking strategies for optimal performance. 
- **End-to-End Testing**: Validate the full pipeline with real-world data and finalize documentation.  |
| Week 6 (Apr 8 – Apr 14)  | Wrap-Up & Review   | Same as Week 5 |

---

### 4. Reference

Melucci, M. (2005) ‘Context modeling and discovery using vector space bases’, *Proceedings of the 14th ACM international conference on Information and knowledge management*, pp. 808–815. doi:10.1145/1099554.1099745.

Merrouni, Z.A., Frikh, B. and Ouhbi, B. (2019) ‘Toward contextual information retrieval: A review and trends’, *Procedia Computer Science*, 148, pp. 191–200. doi:10.1016/j.procs.2019.01.036.

Singh, J.K. and Boursier, P.F. (2024) ‘Adaptive context-aware personalized information retrieval: Enhancing precision with evolutionary machine learning’, *International Journal of Computer Applications*, 186(57), pp. 1–6. doi:10.5120/ijca2024924297.

Tamine, L. and Daoud, M. (2018) ‘Evaluation in contextual information retrieval’, *ACM Computing Surveys*, 51(4), pp. 1–36. doi:10.1145/3204940.

Tourani, A. *et al.* (2024) ‘Capri: Context-aware point-of-interest recommendation framework’, *Software Impacts*, 19, p. 100606. doi:10.1016/j.simpa.2023.100606.

Wan, H. *et al.* (2024) ‘How can personalized context help? exploring joint retrieval of passage and personalized context’, *ICASSP 2024 - 2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)*, pp. 9991–9995. doi:10.1109/icassp48485.2024.10447921.

Zuo, S. *et al.* (2023a) ‘Context-aware query rewriting for improving users’ search experience on e-commerce websites’, *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 5: Industry Track)*, pp. 616–628. doi:10.18653/v1/2023.acl-industry.59.

Zuo, S. *et al.* (2023b) ‘Context-aware query rewriting for improving users’ search experience on e-commerce websites’, *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 5: Industry Track)*, pp. 616–628. doi:10.18653/v1/2023.acl-industry.59.
