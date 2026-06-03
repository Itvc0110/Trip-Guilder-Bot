# Context: Trip-Guilder-Bot (AI Weekend Planner)

This document serves as the **Quality Context and Developer Guide** for **CODEX** (or any agentic AI developer). It outlines the core philosophy of building AI products under uncertainty derived from [HACKATHON_REQUIREMENTS.md](HACKATHON_REQUIREMENTS.md), specifies the product design for the **Trip-Guilder-Bot** (AI Weekend Planner) based on Group 3's [evidence-pack-template.md](02-group-spec/evidence-pack-template.md), [thin-spec-template.md](02-group-spec/thin-spec-template.md), and [synthesis-decide-toolkit.md](02-group-spec/synthesis-decide-toolkit.md), and defines the system architecture, 4 UX paths, and implementation milestones.

---

## 📖 1. Core Philosophy: Designing AI Products for Uncertainty

AI applications differ from traditional software. Software is deterministic, whereas AI is **probabilistic** (exhibits variance, errors, and context sensitivity). Developing an AI product is about **risk management, error routing, and creating feedback loops**.

### 1.1 The Three Layers of Uncertainty
1. **Input Uncertainty**: Users write vague or incomplete queries (e.g., *"lập lịch trình đi chơi cuối tuần"* - lacking duration, child friendly constraints, vehicle details, etc.).
2. **Process Uncertainty**: The agent or system may interpret instructions incorrectly, use tools with errors, or face context length limitations.
3. **Output Uncertainty**: The model might hallucinate, suggest outdated info (e.g., closed restaurants), or present incorrect travel routes with high confidence.

### 1.2 Error Routing Lifecycle: Detect → Route → Recover → Learn
*   **Detect**: Detect low-confidence inputs (e.g., vague prompts) or execution failures (e.g., API errors, missing locations).
*   **Route**: Reroute execution to a safe path (e.g., query clarification prompts, display fallback templates, escalate to human choice).
*   **Recover**: Give users intuitive mechanisms to recover from errors (e.g., drag-and-drop itinerary correction, manual text editing, choosing alternative places).
*   **Learn**: Collect user interactions as learning signals (e.g., logging corrections, tracking approval rates, saving selected options) to continuously improve prompts and datasets.

### 1.3 Automation vs. Augmentation
*   **Augmentation (Selected Path)**: AI draft or suggestion engine. The human remains in the loop as the reviewer, editor, and final decider. 
    *   *Why?* Travel planning involves highly personal constraints (kid's mood, traffic, sudden weather changes). The cost of a bad automated booking is high, while the cost of rejecting a bad AI suggestion is low if the UX makes correction simple.
*   **Agency Progression**: Start with Augmentation (V1 Suggestion & V2 Copilot) before attempting V3 (Automation) after collecting substantial real-use interaction data.

### 1.4 Precision vs. Recall Tradeoff
*   In travel planning, **Recall is prioritized** (finding a wide range of relevant spots to keep the itinerary exciting), provided the UX gives the user tools to filter and correct.
*   For critical steps (e.g., adding to Calendar or calculating transit times), **Precision is prioritized** via structured confirmations.

---

## 🛠️ 2. Product Specification & Build Slice (AI Weekend Planner)

### 2.1 Target User & Pain Statement
*   **Target User**: Parents with young children (3–10 years old) or groups of young friends, planning a weekend trip/outing in Hanoi.
*   **Pain Statement (Grounded in Evidence)**: 
    *   Google AI Overview returns static, short text lists (often only covering a single morning) with no interactive maps, zero calendar sync, and no check on user constraints (vehicle type, child-friendliness).
    *   Users must copy-paste details across Google Search, Maps, Calendar, Notes, and messaging chats to plan and coordinate.
*   **Analog Pattern (Inspiration)**: *Stippl AI Travel Planner* (converts inputs to timeline, integrates drag-drop reordering, maps, and calendar sync).

### 2.2 The Build Slice (Hackathon Scope)
The prototype must showcase a focused slice showing the end-to-end loop:
> **User inputs weekend trip criteria** $\rightarrow$ **AI generates structured timeline** $\rightarrow$ **Interactive map displays places** $\rightarrow$ **User can drag-and-drop to reorder or edit times** $\rightarrow$ **User can export/mock sync to Calendar** $\rightarrow$ **App logs user corrections to console**.

---

## 🎨 3. The Four UX Paths & Fallback Designs

| Path | Scenario | System UX Response |
| :--- | :--- | :--- |
| **1. Happy Path** | User inputs complete query (e.g., *“Gia đình 4 người, trẻ 7 tuổi, xuất phát Hà Nội, thích thiên nhiên, 2 ngày, ô tô”*). | AI generates a clean, structured timeline with hours. Places display on the map iframe. "Add to Google Calendar" button is active. |
| **2. Low‑Confidence Path** | User inputs vague query (e.g., *“Đi chơi cuối tuần đi”* or *“Đi đâu cũng được”*). | AI detects ambiguity. Instead of guessing, it displays a clarification wizard with 3 choice buttons: *(1) Outdoor/Nature, (2) Indoor/Entertainment, (3) Cafe/Food Tour*. |
| **3. Failure Path** | User inputs an unavailable/extremely niche preference (e.g., *“xem chim hoàng yến trong công viên”*). | AI returns a graceful message: *"Rất tiếc, chưa tìm thấy địa điểm phù hợp. Bạn có muốn thử các địa điểm thiên nhiên ngoài trời nổi bật tại Hà Nội không?"* and displays 3 fallback suggestions: **Công viên Thống Nhất, Hồ Tây, Vườn bách thú**. |
| **4. Correction Path** | User changes dates, deletes a spot, or reorders the schedule. | App updates the timeline immediately, updates the map view, recalculates travel slots, and prints a structured JSON correction log in the browser console. |

---

## 🏗️ 4. System Architecture & Data Schema

### 4.1 Technology Stack
1.  **Frontend**: Vanilla HTML5, Vanilla JavaScript (ES6+), and Premium Vanilla CSS.
    *   *Design Aesthetics*: Harmonious dark/light theme, modern typography (Google Fonts Outfit or Inter), smooth micro-animations, glassmorphism card styling, responsive design. **Absolutely no basic or ugly UI templates.**
2.  **AI Engine Mock / Local Prompt Runner**:
    *   Uses a client-side mock LLM database mapping typical query combinations to structured JSON responses, or hooks to a simple local API.
    *   Outputs structured JSON containing: name, coordinates, description, time window, child-friendly score, fallback places.
3.  **Google Maps Mock Integration**:
    *   Embedded responsive iframe map (Google Maps Embed API or Leaflet JS Map with coordinates) pointing to the suggested locations.
4.  **Google Calendar Integration**:
    *   Export feature: Generates a `.ics` file for download, or opens a mock Google Calendar page pre-filled with the itinerary details.

### 4.2 Learning Loop Event Log Schema
Every edit, drag-and-drop, delete, or fallback trigger must output a log to the developer console in this format:
```json
{
  "timestamp": "2026-06-03T16:50:00Z",
  "event_type": "itinerary_reordered | spot_deleted | spot_edited | fallback_triggered",
  "data": {
    "spot_id": "zoo_hanoi",
    "old_time_slot": "09:00 - 11:00",
    "new_time_slot": "10:00 - 12:00",
    "reason_if_any": "user_drag_drop",
    "user_context": {
      "has_kids": true,
      "num_people": 4
    }
  }
}
```

---

## 🎯 5. System Design Milestones & Definition of Done (DoD)

CODEX must implement and check the following milestones sequentially:

### Milestone 1: Project Setup, Layout & Design System
*   [ ] Configure project structure: `index.html`, `index.css`, `app.js`, and `data.js` (mock database).
*   [ ] Build the design system in `index.css` featuring curated palettes (e.g. HSL tailored styles), Outfit font, card styling, and hover transition scales.
*   *DoD Check*: UI matches modern web aesthetics (no default browser elements, custom scrollbars, cohesive colors).

### Milestone 2: Clarification Wizard & Low-Confidence Flow (Path 2)
*   [ ] Implement input field and query classification logic.
*   [ ] Build the interactive clarification UI that triggers when input length is low or keywords are missing.
*   *DoD Check*: Entering *"đi chơi đi"* correctly displays the 3 multiple-choice options.

### Milestone 3: Itinerary Generator & Maps Mock (Path 1 & 3)
*   [ ] Integrate mock database lookup (or LLM call) matching input parameters (activities, child ages) to structured itineraries.
*   [ ] Display the generated timeline in an interactive schedule board (hour-by-hour cards with badges).
*   [ ] Integrate the Leaflet.js or Google Maps iframe showing markers for the itinerary locations.
*   [ ] Implement Path 3 (Failure Mode): Triggering a niche request fallback shows the default 3 outdoor spots.
*   *DoD Check*: Happy path query yields structured cards + marker map; niche query yields fallback suggestions gracefully.

### Milestone 4: Drag-and-Drop / Timeline Correction (Path 4)
*   [ ] Add drag-and-drop HTML5 API support to reorder cards on the timeline, or provide simple Up/Down edit buttons.
*   [ ] Automatically recalculate schedule hours when cards are reordered or a card is deleted.
*   [ ] Wire up console logging for every reorder action according to the event log schema in Section 4.2.
*   *DoD Check*: Dragging an afternoon spot to the morning swaps their hours, updates the map sequence, and logs the change to the console.

### Milestone 5: Google Calendar Sync & Final QA
*   [ ] Implement the export functionality: generate a valid `.ics` file containing the events, or build a mock "Add to Google Calendar" pre-filled event link generator.
*   [ ] Run manual end-to-end tests for all 4 paths.
*   [ ] Ensure mobile responsiveness.
*   *DoD Check*: Clicking the calendar button prompts a calendar file download or opens the pre-filled mock calendar link.
