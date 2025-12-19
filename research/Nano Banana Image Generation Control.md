# **Strategic Implementation of Generative AI for High-Fidelity E-Commerce Imagery: Governance, Architecture, and Optimization of the "Nano Banana" Ecosystem**

## **1\. Executive Summary and Strategic Context**

The digital commerce landscape is currently navigating a profound inflection point, transitioning from traditional, capital-intensive asset production to dynamic, algorithmic generation. For enterprise retailers, particularly those managing extensive stock-keeping units (SKUs) or regulated goods, the ability to automate the transformation of static "ghost mannequin" product shots into hyper-realistic, lifestyle-in-use imagery represents a decisive competitive advantage. This capability not only accelerates time-to-market but also enables a level of personalization previously unattainable—contextualizing products for specific user demographics, seasons, or use cases dynamically. However, this transition is fraught with technical and ethical complexities. The deployment of generative models such as Google's "Nano Banana" (Gemini 2.5 Flash Image) and "Nano Banana Pro" (Gemini 3 Pro Image Preview) requires a sophisticated understanding of model architecture, parameter optimization, and, most critically, rigorous semantic governance.

The user's objective—to generate conversion-driving imagery for Product Detail Pages (PDPs) while enforcing strict safety protocols around regulated items (e.g., firearms, tactical gear) and ensuring physical realism—demands a departure from standard "text-to-image" prompting. It requires the implementation of a "Generative Manufacturing" pipeline. In this paradigm, the AI model is not treated as a creative artist but as a stochastic engine constrained by rigid physical and semantic laws. The challenge lies in balancing the model's creative potential (to make a scene look realistic and engaging) with the absolute necessity of adherence to the "ground truth" of the product and the safety policies of the brand. For instance, ensuring a "finger is not on the trigger" or that "a child is never present" in a scene involving tactical equipment is not merely a stylistic preference but a compliance imperative.

This report provides an exhaustive technical analysis of the Nano Banana ecosystem, detailing the specific parameters, architectural nuances, and governance frameworks required to build such a pipeline. It draws upon deep technical documentation and industry best practices to outline a comprehensive strategy for deploying Gemini 3 Pro’s advanced reasoning capabilities ("Thinking" models) to achieve high-fidelity, safe, and commercially viable imagery.1 By prioritizing "Identity Locking" through multi-modal reference inputs and establishing a "Hierarchical Grounding Protocol" to resolve conflicts between visual data and textual descriptions, enterprises can mitigate the risk of hallucination and ensure that the digital asset remains a faithful representation of the physical product.

## ---

**2\. Architectural Analysis of the Nano Banana Ecosystem**

To effectively leverage the parameters available for image generation, one must first understand the distinct architectures of the models within the "Nano Banana" family. These are not merely different versions of the same software but represent fundamentally different approaches to the generative process, each optimized for specific stages of the e-commerce content supply chain.

### **2.1 The Dichotomy of Speed vs. Reasoning**

The ecosystem is bifurcated into two primary models, each serving a distinct operational role. Understanding this dichotomy is the first step in optimizing for both cost and quality.

#### **Gemini 2.5 Flash Image ("Nano Banana")**

The Gemini 2.5 Flash Image model (gemini-2.5-flash-image) acts as the high-throughput engine of the ecosystem. Architecturally, it is optimized for low-latency generation, making it suitable for tasks where volume and speed take precedence over complex spatial reasoning or strict adherence to intricate safety logic.1 In an e-commerce context, this model is ideal for rapid prototyping, background texture generation, or creating variations of non-regulated, simple products where the risk of safety violations is negligible. However, its streamlined architecture means it lacks the deep "cognitive" buffer required to process conflicting constraints (e.g., "show a gun but make it look safe") with the same reliability as its Pro counterpart. It operates closer to a traditional diffusion model, mapping text to pixels with direct probabilistic efficiency.

#### **Gemini 3 Pro Image Preview ("Nano Banana Pro")**

The Gemini 3 Pro Image Preview (gemini-3-pro-image-preview) represents the frontier of generative capability, distinguished by its integration of a "Thinking" process or reasoning engine.1 Unlike standard models that move directly from prompt to generation, the Pro model engages in an intermediate phase of logical processing. When presented with a complex instruction—such as "generate a lifestyle shot of a tactical backpack on a forest floor, ensure the lighting suggests dawn, do not occlude the zippers, and strictly exclude any human figures"—the model first formulates a plan. This internal monologue allows it to verify constraints against safety policies and physical laws before a single pixel is rendered.3

For the user's specific use case involving regulated goods and strict semantic governance (e.g., weapon safety), the Gemini 3 Pro architecture is the only viable candidate for final asset production. Its ability to "reason" allows it to understand the semantic difference between "active combat" (prohibited) and "safe storage" (allowed), a nuance that faster, shallower models often miss, leading to safety violations. Furthermore, its expanded context window, which supports up to 14 reference images, provides the necessary bandwidth for "Identity Locking," allowing the model to ingest multiple angles of a ghost mannequin shot to build a comprehensive 3D understanding of the product.3

### **2.2 The "Thinking" Process: A Technical Advantage for Governance**

The "Thinking" capability of Gemini 3 Pro is not a marketing term but a functional architectural component that can be leveraged for governance. In the API, this is often controlled or influenced by parameters related to "reasoning effort" or "thinking level".4 When this parameter is maximized, the model allocates more computational resources to the pre-generation analysis phase.

For e-commerce, this "Thinking" phase serves as an automated quality assurance step. Before generating an image of a firearm accessory, the model evaluates the prompt's negative constraints ("no kids," "no active combat"). It effectively runs a simulation of the prompt's requirements, identifies potential conflicts (e.g., "a lifestyle shot usually implies a user, but the prompt forbids humans"), and resolves them (e.g., "I will frame this as a still-life product shot on a range bag instead"). This capability drastically reduces the rate of "reject" images that violate safety policies compared to older generation models, which would often hallucinate a human hand holding the weapon simply because the training data for "tactical gear" strongly correlates with "soldiers."

### **2.3 Context Window and Multimodal Ingestion**

A critical limitation of earlier generative models was their inability to maintain product fidelity. They would generate a *category* of product (e.g., "a backpack") rather than the *specific* product (e.g., "The Osprey Talon 22 in red"). The Nano Banana Pro architecture addresses this through a massive multimodal context window. By accepting up to 14 reference images 2, the model does not need to rely on its internal training data to "guess" what the product looks like. Instead, it uses the provided reference images as a visual anchor. This architectural feature is the cornerstone of the "Identity Locking" workflow, allowing the ghost mannequin image to serve as the immutable ground truth for the product's geometry and features.

## ---

**3\. Comprehensive Analysis of API Parameters**

To operationalize these models, one must master the API parameters. These controls are the levers by which a developer or product manager governs the output, ensuring it meets the stringent requirements of brand safety and physical realism.

### **3.1 Core Configuration Parameters**

The GenerateContentConfig object is the primary interface for configuring the model's behavior.

#### **model**

This parameter selects the underlying engine. For the defined use case—high-fidelity PDP imagery of regulated goods—the only acceptable value is gemini-3-pro-image-preview. The 2.5 Flash model should be reserved for low-risk tasks or generating background textures that will be composited later. Using the Pro model ensures access to the "Thinking" process and the extended reference image capacity.1

#### **media\_resolution**

This parameter controls the token allocation for input images. The available values typically range from MEDIA\_RESOLUTION\_LOW to MEDIA\_RESOLUTION\_HIGH (or similar enum values depending on the specific SDK version).

* **Optimization Strategy**: For ghost mannequin to lifestyle transformation, this must strictly be set to the highest available setting (e.g., MEDIA\_RESOLUTION\_HIGH). This forces the model to analyze the input ghost image with maximum granularity, capturing subtle details like fabric weave, stitching patterns, and small text labels.6 Reducing this parameter to save on latency or cost will result in "smoothing" artifacts where distinct product features are lost or hallucinated away.

#### **aspect\_ratio**

This controls the dimensions of the generated canvas.

* **Optimization Strategy**: This should be programmatically set to match the specific layout requirements of the e-commerce platform's PDP. Common standards include 3:4 (vertical) for fashion and apparel, 1:1 (square) for marketplaces like Amazon, and 16:9 for hero banners. Generating at the correct aspect ratio is crucial because post-generation cropping can inadvertently remove key product details or ruin the composition's balance. The model composes the scene *within* the frame; changing the frame later destroys that composition.7

#### **image\_size or sample\_count**

While basic, these parameters dictate the output quality and variety.

* **Optimization Strategy**: Always request the maximum resolution (e.g., 4096 or 4K for Pro) to ensure the asset is future-proof and supports zoom functionality on the web. Regarding sample\_count (generating multiple images per prompt), a batch size of 4 is recommended. AI generation is stochastic; generating a single image increases the risk of a random artifact ruined the shot. Generating a batch allows for post-generation selection of the best "physics compliance".2

### **3.2 Advanced Governance Parameters**

These parameters are the primary tools for enforcing the safety and semantic requirements (e.g., "no kids with guns").

#### **reasoning\_effort (Gemini 3 Pro)**

This parameter (sometimes referred to as thinking\_level) controls the depth of the model's internal monologue.

* **Optimization Strategy**: Set to HIGH for all regulated goods workflows. This increases latency but is essential for safety. It forces the model to explicitly process negative constraints. When the prompt says "Ensure the trigger finger is indexed," a high reasoning effort ensures the model checks its own plan against this rule. Low reasoning effort relies more on training correlations, which often include unsafe handling practices found in internet data.4

#### **person\_generation**

This parameter offers a binary or trinary switch for human presence (e.g., dont\_allow, allow\_adult, allow\_all).

* **Optimization Strategy**:  
  * **For Product-Only Shots**: Set strictly to dont\_allow. This is the most robust way to ensure "no kids" and "no unsafe handling" because it removes the human element entirely. If the prompt requests a "lifestyle" scene, the model will generate a "still life" setup (e.g., the product on a table) rather than a person holding it.  
  * **For Lifestyle-with-Model Shots**: Set to allow\_adult. Note that the Gemini ecosystem has strict internal safety layers that default to blocking the generation of children in many contexts. However, explicitly setting this parameter reinforces the constraint.9

#### **safety\_settings (The Enum Framework)**

The API exposes comprehensive safety filters based on harm categories: HARM\_CATEGORY\_HARASSMENT, HARM\_CATEGORY\_HATE\_SPEECH, HARM\_CATEGORY\_SEXUALLY\_EXPLICIT, and HARM\_CATEGORY\_DANGEROUS\_CONTENT. Each category can be tuned with a threshold: BLOCK\_NONE, BLOCK\_ONLY\_HIGH, BLOCK\_MEDIUM\_AND\_ABOVE, and BLOCK\_LOW\_AND\_ABOVE.10

* **Optimization Strategy for Regulated Goods**: This requires a nuanced approach. Setting HARM\_CATEGORY\_DANGEROUS\_CONTENT to BLOCK\_LOW\_AND\_ABOVE (the strictest setting) creates a high risk of false positives for a retailer selling tactical gear or knives. The model might classify a picture of a "survival knife" as dangerous content and block the generation entirely.  
  * **Recommended Configuration**: Set HARM\_CATEGORY\_DANGEROUS\_CONTENT to BLOCK\_MEDIUM\_AND\_ABOVE or BLOCK\_ONLY\_HIGH. This allows the *object* (the knife/gun) to be generated but relies on the **System Instructions** and **Prompt Engineering** to govern the *context* (ensuring it is not being used in a violent manner). This shifts the burden of safety from a blunt classifier to the more sophisticated reasoning engine of the Pro model.

### **3.3 Visual Grounding Parameters**

#### **google\_search\_grounding**

This parameter allows the model to use Google Search to verify facts.2

* **Optimization Strategy**: This is a powerful tool for preventing hallucination of product *context*, but it must be used carefully to avoid overriding the *visual* truth.  
  * **Use Case**: Enable this when the prompt includes technical jargon (e.g., "MOLLE webbing," "Picatinny rail"). The model can search to understand what these terms mean, ensuring it places the product in a context that makes sense for those features.  
  * **Risk**: If the product is unreleased or proprietary, the search tool might retrieve images of *competitor* products and hallucinate their features onto yours.  
  * **Mitigation**: Use explicit prompting to prioritize the visual reference image over search results for the object's morphology, while using search results for the environmental context.

## ---

**4\. The "Ghost Mannequin to Lifestyle" Pipeline: A Technical Workflow**

Converting a sterile ghost mannequin shot into a vibrant, high-converting lifestyle image is the core operational goal. This section details the step-by-step pipeline, emphasizing the techniques to maintain product fidelity and realistic physics.

### **4.1 Input Data Strategy and Pre-processing**

The quality of the output is deterministically linked to the quality and structure of the input. A single ghost image is often insufficient for a 3D understanding.

#### **The "Hollow" Problem**

Ghost mannequin images are typically "hollow"—showing the inside of the neck or the back of the waist. Simply compositing this onto a generated model looks artificial because the human body would fill those voids.

* **Correction Strategy**: For apparel, utilizing a specialized "Virtual Try-On" model (like Vertex AI's virtual-try-on-preview) is superior to generic image generation.11 However, for hard goods (backpacks, helmets, tactical vests) or non-fitted apparel (gloves, scarves), Gemini 3 Pro is highly effective.  
* **Preprocessing**: Ensure the ghost image has a clean alpha channel (transparent background). While Gemini can handle white backgrounds, transparency reduces the cognitive load on the model to "segment" the object, allowing it to focus more resources on lighting and integration.

#### **Multi-Angle Ingestion**

Research snippet 3 highlights that Gemini 3 Pro supports up to 14 reference images.

* **Tactical Advantage**: Do not limit the input to the main ghost shot. Upload the front, back, side profile, and specific detail shots (e.g., a macro shot of the fabric texture or logo).  
* **Prompting**: Explicitly reference these inputs in the prompt: "Using Reference Image 1 as the primary geometry and Reference Image 2 as the texture guide..." This gives the model a 360-degree understanding, significantly reducing the chance of it hallucinating the side profile of a product it can only see from the front.

### **4.2 The "Identity Locking" Protocol**

"Identity Locking" is the process of forcing the model to reproduce the reference object exactly, rather than generating a "similar" object.

* **Prompt Structure for Locking**: The prompt must explicitly de-prioritize the model's creative freedom regarding the object.  
  * *Example Instruction*: "OBJECT PERMANENCE: The product depicted in the reference image is the Ground Truth. You are a photographer, not a designer. You must not alter the shape, color, logo placement, or features of the product. Your creative scope is limited strictly to the lighting, background, and camera angle."  
* **Resolving Text-Visual Conflicts**: The user noted a risk where "product information could talk about features but ghost images do not show those features."  
  * **Hierarchical Grounding Protocol**: To solve this, the prompt must define a hierarchy of truth.  
    * **Rule**: "If the text description conflicts with the visual reference, the Visual Reference takes precedence for the object's appearance. The Text Description takes precedence for the environment."  
    * *Scenario*: If the text says "waterproof" but the image shows a mesh vent, the model must render the mesh vent (visual truth) but place the product in a rainy environment (textual truth implies wet conditions), rather than hallucinating a rubber seal over the vent.

### **4.3 Physics and Realism Engineering**

To satisfy the requirement that the "product is not hanging in the air," one must prompt for physical interaction, not just visual placement.

* **Contact Shadow Engineering**: The most common giveaway of AI imagery is the "floating" effect caused by poor ambient occlusion.  
  * **Prompt Tactic**: "PHYSICS ENGINE: The object has mass and weight. Render realistic contact shadows where the object meets the surface. The bottom of the object should interact with the surface texture (e.g., depressing the grass, sitting flush on concrete). Do not render the object floating."  
* **Lighting Consistency**: The lighting on the product (from the ghost shot) often conflicts with the generated environment.  
  * **Prompt Tactic**: "LIGHTING MATCH: Analyze the lighting vectors on the reference object. Construct an environment with lighting sources that match these vectors to ensure seamless integration. If the reference is flat-lit, introduce a 'studio lighting' setup in the environment to justify the even illumination."

## ---

**5\. Governance and Safety: The "Gun and Kid" Problem**

For a retailer dealing with regulated goods, safety is not just about avoiding "Not Safe For Work" (NSFW) content; it is about adherence to specific, nuanced safety protocols. A picture of a child holding a toy gun might be acceptable for a toy store but is a critical violation for a tactical gear retailer. A picture of a finger inside a trigger guard is a violation of basic firearm safety rules. Governing these semantic nuances requires a multi-layered approach.

### **5.1 Layer 1: System Instructions as the "Constitution"**

Gemini 3 Pro supports **System Instructions**—a meta-prompt that persists across all interactions and overrides standard user prompts. This is the ideal place to encode the "Brand Safety Constitution".12

**Table 1: Example System Instruction Architecture for Regulated Goods**

| Rule Category | System Instruction Text (Verbatim to Model) | Rationale |
| :---- | :---- | :---- |
| **Minor Safety** | "CORE DIRECTIVE: You are strictly prohibited from generating images that depict children, toddlers, or minors in the presence of firearms, tactical gear, or knives. All human figures must be clearly identifiable as adults (30+ years)." | Establishes a hard demographic floor. Specifying "30+ years" pushes the model away from ambiguous "young adult" generations. |
| **Trigger Discipline** | "SAFETY PROTOCOL: For any firearm imagery, the trigger finger must ALWAYS be straight and indexed along the frame (slide). NEVER depict a finger inside the trigger guard. If hand placement cannot be verified as safe, do not generate hands." | Addresses the specific "finger on trigger" constraint. Giving the model an "out" (do not generate hands) reduces failure rates. |
| **Muzzle Discipline** | "DIRECTIONAL SAFETY: Muzzles must be pointed in a safe direction (downrange or neutral/ground). Never point a muzzle at the camera or another person." | Enforces basic gun safety rules in the visual composition. |
| **Contextual Safety** | "SCENARIO RESTRICTION: Do not depict active combat, aggression, or violence. The context must be 'Safe Storage', 'Maintenance', 'Range Practice', or 'Retail Display'. No muzzle flashes or casings in air." | Solves the "no active combat" requirement by defining allowed safe contexts. |

### **5.2 Layer 2: Semantic Negative Constraints**

While the API has specific fields for negative prompts, Gemini 3 Pro's reasoning engine responds exceptionally well to natural language constraints embedded in the main prompt.

* **Constraint Block**:  
  "NEGATIVE CONSTRAINTS (STRICT ADHERENCE REQUIRED):  
  * NO children, minors, or schools.  
  * NO blurred faces or distorted limbs.  
  * NO floating objects or defiance of gravity.  
  * NO hallucinations of features not present in the reference.  
  * NO text overlays or watermarks unless explicitly requested."

### **5.3 Layer 3: The "Soft Governance" of Reasoning**

By using the reasoning\_effort="high" parameter, we leverage the model's "Thinking" process to enforce these rules. When the model receives a request for a "lifestyle shot," its internal reasoning trace might look like this:

* *Internal Monologue*: "User wants a lifestyle shot. Standard training data suggests a soldier in combat. System Instruction forbids combat and mandates safety. I will instead generate a 'range day' scenario with the firearm resting on a bench, action open, creating a safe but aspirational lifestyle image."

This "soft governance" is often more effective than hard filters because it redirects the model's creativity rather than simply blocking it, resulting in a usable asset that meets safety standards.

## ---

**6\. Optimizing for Conversion: Aesthetic Tuning**

To drive conversion on PDPs, the images must not only be safe and accurate but also visually compelling. They must look like high-end photography, not AI generations.

### **6.1 The Photographic Triad Strategy**

To achieve photorealism, the prompt must speak the language of a Director of Photography (DoP), not a data scientist.

* **Optical Physics**: Define the lens and sensor.  
  * *Tactic*: Instead of "close up," use "Macro shot captured with a 100mm f/2.8 lens." This instructs the model on exactly how to handle depth of field and compression.  
  * *Tactic*: "Shot on 35mm film stock, ISO 400." This adds subtle grain and noise, which counteracts the "plastic/smooth" look common in AI images.  
* **Lighting Architecture**: Define the light sources.  
  * *Tactic*: "Key light softbox at 45 degrees, cool rim light separating the object from the background, negative fill on the right." This creates dimensionality and drama.  
* **Materiality**: Define the imperfections.  
  * *Tactic*: Real life is messy. Prompt for "Subtle dust motes in the air, microscopic texture on the table surface, realistic weathering on the wood." These imperfections trick the human eye into accepting the image as real.

### **6.2 Visual Hierarchy and Composition**

For a PDP, the product must be the hero.

* **Prompt Tactic**: "Composition: Central framing. The product should occupy 60% of the frame. Use 'leading lines' in the background texture to draw the eye to the product logo. Background should be de-emphasized via bokeh (blur)."

### **6.3 Contextual Relevance via Metadata**

Use the product metadata to drive the scene generation.

* *Input*: Product is a "Waterproof Hiking Boot".  
* *Prompt*: "Environment: Wet slate rock surface, distinct water droplets on the surface (to demonstrate waterproofing), moody overcast lighting."  
* This aligns the visual story with the product's value proposition (waterproofing), directly driving conversion by visualizing the feature.

## ---

**7\. Implementation Strategy and Operationalization**

Deployment of this technology requires a robust operational framework involving API integration, Quality Assurance (QA), and cost modeling.

### **7.1 Technical Integration Workflow**

**Step 1: Ingestion & Analysis**

* System ingests the ghost image and metadata.  
* A pre-processing script standardizes the image (resizing, format conversion) and extracts key visual features (color code, aspect ratio).

**Step 2: Prompt Construction**

* The system dynamically builds the prompt by combining:  
  1. The immutable **System Instruction** (Safety Constitution).  
  2. The **Product Description** (converted into visual descriptors).  
  3. The **Scenario Template** (e.g., "Forest Floor").  
  4. The **Constraint Block** (Negative constraints).

**Step 3: Generation (The "Pro" Call)**

* API call is made to gemini-3-pro-image-preview.  
* Parameters: reasoning\_effort="high", media\_resolution="high", sample\_count=4.  
* Reference images are attached for Identity Locking.

**Step 4: Automated Safety Audit (The "Flash" Check)**

* Before a human sees the image, pass the generated result to a secondary vision model (e.g., Gemini 1.5 Flash).  
* *Audit Prompt*: "Analyze this image. Does it contain a child? Is there a finger inside a trigger guard? Is the product floating? Output strictly JSON: {'safe': boolean, 'physics\_ok': boolean}."  
* If the audit fails, the image is discarded and regenerated with a higher "guidance scale" or modified prompt.

**Step 5: Human-in-the-Loop (HITL)**

* For regulated goods, a human review is mandatory. The AI acts as a force multiplier, presenting the human with 4 "pre-approved" options, reducing the workload from creation to mere selection.

### **7.2 Cost and Performance Modeling**

* **Nano Banana (Flash)**: Use this model for generating the *backgrounds* or for internal ideation tools. It is cost-effective but lacks the safety reasoning for final regulated assets.  
* **Nano Banana Pro**: Use this exclusively for the final render. While the cost per API call is higher, the "Identity Locking" and "Safety Reasoning" capabilities drastically reduce the "reject rate."  
  * *ROI Calculation*: If a traditional photoshoot costs $500 per SKU and Nano Banana Pro costs $0.10 per image, even with a 50% reject rate requiring regeneration, the cost savings are orders of magnitude high. The primary cost driver becomes the *governance setup* rather than the generation itself.

### **7.3 Future Outlook: The "Digital Twin"**

As the "Nano Banana" ecosystem evolves, we anticipate a shift towards "Digital Twin" training. Rather than passing reference images with every prompt, brands will likely fine-tune a dedicated adapter (LoRA) on their entire catalog. This would allow the model to inherently "know" the brand's aesthetic and safety rules without explicit prompting. However, until such features are generally available and audit-compliant for regulated goods, the "System Instruction \+ Reference Image" workflow remains the gold standard for safe, high-fidelity e-commerce generation.

## ---

**8\. Conclusion**

The transition to AI-generated e-commerce imagery is not merely a technological upgrade but a fundamental shift in content operations. By utilizing the specific architectures of the Nano Banana ecosystem—leveraging the speed of Flash for iteration and the reasoning power of Pro for final execution—retailers can achieve the "holy grail" of personalization at scale.

However, the success of this initiative rests entirely on **Governance**. The ability to prevent a "kid with a gun" image is not a feature of the model but a result of the *architecture* built around the model. It requires the rigid implementation of System Instructions, the strategic use of reasoning parameters, and a pipeline that enforces "Identity Locking" to preserve product truth. When these elements are synchronized, the result is a content engine that drives conversion through hyper-realistic, safe, and brand-aligned imagery, indistinguishable from the work of a professional studio.

### **References**

* 1 Gemini API Documentation: Model Architecture & Capabilities.  
* 2 Google Cloud Blog: Nano Banana Pro Enterprise Features.  
* 3 Prompt Engineering Guide: Identity Locking & Reference Images.  
* 10 Safety Settings Enum Documentation.  
* 4 Reasoning Effort & Thinking Parameters.  
* 12 System Instructions Implementation Guide.  
* 6 Media Resolution Token Limits.  
* 11 Vertex AI Virtual Try-On Technical Specs.

#### **Works cited**

1. Nano Banana (Image generation) | Gemini API | Google AI for ..., accessed December 18, 2025, [https://ai.google.dev/gemini-api/docs/nanobanana](https://ai.google.dev/gemini-api/docs/nanobanana)  
2. Nano Banana Pro available for enterprise | Google Cloud Blog, accessed December 18, 2025, [https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-pro-available-for-enterprise](https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-pro-available-for-enterprise)  
3. Nano-Banana Pro: Prompting Guide & Strategies \- DEV Community, accessed December 18, 2025, [https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n](https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n)  
4. Gemini \- Google AI Studio \- LiteLLM, accessed December 18, 2025, [https://docs.litellm.ai/docs/providers/gemini](https://docs.litellm.ai/docs/providers/gemini)  
5. Image generation with Gemini (aka Nano Banana & Nano Banana Pro) | Gemini API | Google AI for Developers, accessed December 18, 2025, [https://ai.google.dev/gemini-api/docs/image-generation](https://ai.google.dev/gemini-api/docs/image-generation)  
6. Media resolution | Gemini API \- Google AI for Developers, accessed December 18, 2025, [https://ai.google.dev/gemini-api/docs/media-resolution](https://ai.google.dev/gemini-api/docs/media-resolution)  
7. Nano Banana Pro – Gemini AI image generator and photo editor, accessed December 18, 2025, [https://gemini.google/ca/overview/image-generation/?hl=en-CA](https://gemini.google/ca/overview/image-generation/?hl=en-CA)  
8. Gemini 3 Pro Image API: Complete Developer Guide 2025 (Nano Banana Pro) \- Cursor IDE, accessed December 18, 2025, [https://www.cursor-ide.com/blog/gemini-3-pro-image-api](https://www.cursor-ide.com/blog/gemini-3-pro-image-api)  
9. Image generation API \- Vertex AI \- Google Cloud Documentation, accessed December 18, 2025, [https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api)  
10. Safety settings | Gemini API | Google AI for Developers, accessed December 18, 2025, [https://ai.google.dev/gemini-api/docs/safety-settings](https://ai.google.dev/gemini-api/docs/safety-settings)  
11. Virtual Try-On Preview 08-04 | Generative AI on Vertex AI \- Google Cloud Documentation, accessed December 18, 2025, [https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/virtual-try-on-preview-08-04](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/virtual-try-on-preview-08-04)  
12. Gemini 3 Pro Image Preview – Vertex AI \- Google Cloud Console, accessed December 18, 2025, [https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemini-3-pro-image-preview](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemini-3-pro-image-preview)  
13. Gemini for safety filtering and content moderation | Generative AI on Vertex AI, accessed December 18, 2025, [https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-for-filtering-and-moderation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-for-filtering-and-moderation)