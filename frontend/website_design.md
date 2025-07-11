 and roles through dynamic state management and modal overlays. The design features a sophisticated, professional interface that seamlessly transitions between customer and business owner experiences.

The main page serves as a dynamic container that renders different "views" based on user authentication state and role. For unauthenticated users, it displays a clean authentication interface with login/register options. Once authenticated, customers see a restaurant selection interface that transforms into their chosen restaurant's ordering system with multiple interaction modes (chatbot, standard menu, voice agent). Business owners access a comprehensive dashboard for menu management, orders, and analytics.

The design uses a cohesive navigation system that adapts contextually - showing different options based on user role and current view. All interactions happen within modals and dynamic content areas, creating a fluid single-page experience while maintaining the feeling of a full application.

The ordering interfaces are the centerpiece, featuring three distinct modes: an AI chatbot interface with natural language processing, a traditional menu-based ordering system, and an innovative voice agent interface. Each mode maintains consistent branding while offering unique interaction patterns suited to different customer preferences.

The business dashboard integrates seamlessly with the customer experience, allowing real-time order management, menu updates, and comprehensive analytics. The design maintains professional aesthetics throughout while ensuring each component serves its specific functional purpose.
</website_design>

<high_level_design>
1. Color palettes:
   - Primary: Emerald (#10b981) - Professional, modern, associated with growth and efficiency
   - Neutral: Sophisticated grays (#f8fafc, #64748b, #1e293b) - Clean, readable, timeless
   - Usage: Emerald for primary actions, CTAs, success states; grays for backgrounds, text, borders

2. Typography: 
   - Font family: Inter - Professional, highly readable, excellent for both text and data display
</high_level_design>

<components>

<create_component>
<file_path>src/components/auth-interface.tsx</file_path>
<design_instructions>Create a sophisticated authentication interface with tabbed login/register forms. Use Inter font family and emerald accent color. Include fields for email, password, and for registration: name, role selection (customer/business owner), and terms acceptance. Style with clean form inputs using shadcn/ui components, subtle shadows, and proper spacing. Include social login options and forgot password link. Use Card component as base with clean typography hierarchy.</design_instructions>
</create_component>

<create_component>
<file_path>src/components/restaurant-selection.tsx</file_path>
<design_instructions>Design a clean restaurant selection grid for customers. Display restaurant cards with images, names, ratings, cuisine types, and estimated delivery times. Use shadcn/ui Card components with hover effects. Include a search bar at the top and filter options (cuisine type, rating, delivery time). Each restaurant card should have a subtle shadow and clean typography. Use emerald accents for ratings and primary actions. Grid should be responsive with proper spacing.</design_instructions>
</create_component>

<create_component>
<file_path>src/components/ordering-system.tsx</file_path>
<design_instructions>Create a comprehensive ordering interface with three modes: chatbot, standard menu, and voice agent. Include a mode selector at the top using shadcn/ui Tabs. For chatbot mode: show a chat interface with message bubbles, input field, and suggested responses. For standard mode: display categorized menu with items, prices, customization options, and add-to-cart buttons. For voice mode: show a large microphone button, waveform visualization, and transcribed text. Include a persistent cart sidebar with items, quantities, and total. Use emerald for primary actions and clean gray backgrounds.</design_instructions>
</create_component>

<create_component>
<file_path>src/components/business-dashboard.tsx</file_path>
<design_instructions>Design a comprehensive business dashboard with multiple sections accessible via a sidebar navigation. Include: order management with real-time order cards showing status, customer info, and items; menu management with editable item cards, drag-and-drop reordering, and add/edit forms; analytics section with charts and key metrics; stock management with inventory levels and alerts. Use shadcn/ui components like Card, Table, Dialog, and Form. Maintain professional appearance with emerald accents for success states and clear data hierarchy. Include notification badges and status indicators.</design_instructions>
</create_component>

<create_component>
<file_path>src/components/business-onboarding.tsx</file_path>
<design_instructions>Create a multi-step onboarding flow for new business owners using shadcn/ui components. Include steps for: business information (name, address, contact), restaurant details (cuisine type, hours, delivery zones), menu upload (file upload or manual entry), payment setup, and final review. Use a progress indicator at the top showing current step. Each step should be in a clean Card layout with proper form validation. Include back/next navigation and a summary sidebar showing progress. Use emerald for progress indicators and completion states.</design_instructions>
</create_component>

<create_component>
<file_path>src/components/order-tracking.tsx</file_path>
<design_instructions>Design a real-time order tracking interface showing order progress through different stages (confirmed, preparing, ready, out for delivery, delivered). Use a visual timeline with status dots and connecting lines, each stage clearly labeled with timestamps. Include estimated delivery time, delivery driver info (when applicable), live map integration placeholder, and order details summary. Use emerald for completed stages, gray for pending stages. Include notification preferences and contact options. Style with clean cards and professional typography using Inter font.</design_instructions>
</create_component>

</components>