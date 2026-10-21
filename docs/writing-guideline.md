# Paper Writing Guideline (extract)

Source: supervisor's paper-writing guide (38 pages), extracted 2026-10-17 for
this repo. Use together with `docs/prompt.md`.
`docs/prompt.md` controls the voice (student register, anti-AI patterns). This
page controls the structure and the content of each section of the paper
(`IEEE-conference/IEEE-conference.tex`).

Scope note: this extract governs the completed 6-page ICEEICT conference paper
(`IEEE-conference/IEEE-conference.tex`). Its conference-specific length and
section guidance do not govern a future journal manuscript. For Phase 8, follow
the selected journal's current author instructions and include the full methods,
limitations, reproducibility, and required declarations; do not assume a venue
until the roadmap's journal-selection gate is complete.

---

## 1. Title

A research article title should be clear, concise, specific, informative, and
easy to understand.

- Clear: communicates the research topic without ambiguity.
- Concise: avoids unnecessary words.
- Specific: identifies the main problem, method, subject, or contribution.
- Informative: gives readers a good idea of what the paper contains.
- Easy to understand: avoids unnecessary jargon, abbreviations, and complicated
  wording.

Example from the guide:

- Weak: 'An Investigation into the Application of Various Advanced Deep
  Learning Based Computational Techniques for the Purpose of Automated
  Detection of Vegetable Quality'
- Strong: 'Deep Learning for Automated Vegetable Quality Detection'

## 2. Abstract

Answer six questions, in this order.

1. Initialization: what is the research area? Name the broad domain, the topic,
   and the current trend (Machine Learning, then Deep Learning, then Image
   Classification).
2. Research gap: what is missing? Point to limitations, unanswered questions,
   weaknesses, and unexplored areas in existing research. Establish the need
   for the study.
3. Research objective: what do you want to do? State what the work
   investigates, develops, improves, compares, or discovers.
4. Proposed approach: how will you do it? Cover the methodology, models,
   algorithms, experimental design, dataset, and evaluation strategy.
5. Justification: why this method and dataset? Explain why the approach is
   appropriate and necessary, and why it is used instead of existing
   alternatives.
6. Expected or research outcome: what will the work contribute? List the
   expected findings, performance improvement, dataset, model, framework,
   insights, or other contributions.

The guide gives two equivalent formulas:

- Context plus gap plus objective plus method plus rationale plus outcome
  equals a research abstract.
- Research area, gap, objective, method, justification, experiment, outcome,
  contribution.

## 3. Keywords

Pick four to eight important concepts.

1. Research topic: what is the paper mainly about?
2. Research method: the methods, algorithms, or technologies used.
3. Application or domain: where the research is applied.
4. Specific problem: what problem is solved.
5. Standard terminology: use terms researchers actually use. Wrong: 'computer
   method for finding bad vegetables'. Right: 'vegetable defect detection'.
6. Avoid broad terms such as Machine Learning, Artificial Intelligence, or
   Computer Science unless they are genuinely central to the paper.

Formula: research domain plus problem plus method plus application plus
specific technique. Example from the guide: the title 'Real-Time Detection of
Fresh and Defective Vegetables Using Deep Learning' gives the keywords deep
learning, vegetable defect detection, object detection, computer vision,
transfer learning, and agricultural image analysis.

## 4. Introduction (four paragraphs)

Paragraph 1: current state and framing.

- What is currently happening in the research area: existing methods,
  technologies, recent developments, and why the topic matters.
- What is missing: limitations, unresolved challenges, unaddressed problems,
  and the research questions that follow.
- What you want to do and how: the objective and the approach.
- Scope: what the proposed method can do, where it applies, what the dataset
  contains, who can use it, and the boundaries of the scope.

Paragraph 2: merged literature review.

- What previous researchers have done, and the methods, models, datasets, and
  approaches they used.
- The strengths and limitations of existing studies.
- Unresolved issues, and the specific gap that follows from the literature.

Paragraph 3: gap and resolution.

- What was not done, solved, mitigated, or resolved in the literature, and
  why.
- What you want to do and how you will do it.
- Why the chosen method and dataset suit the problem.
- Scope of the proposed method and dataset.

Paragraph 4: contribution.

- The proposed method and dataset, with the contribution stated plainly.

Overall flow from the guide: current state, then existing research plus
critical review plus gap, then what was not solved and why plus what you will
do, then scope of method and dataset plus contribution.

Note: `docs/prompt.md` §10 gives a three-paragraph version of this
introduction with per-claim citation placement. The two describe the same
content with a different split; keep one and compress it to fit the page limit.

## 5. Types of article

1. Method based.
2. Dataset based.
3. Method plus dataset based.

Organization for a method-based article:

1. Introduction
2. Conventional method or methods
3. Proposed method
4. Experiments (4.1 experimental setup, 4.2 corpus or dataset)
5. Results
6. Conclusion
7. Author contribution, Declaration (funding, data availability, competing
   interests), Acknowledgements, Reference.

Organization for a dataset-based article:

1. Introduction
2. Dataset or corpus (2.1 data collection, 2.2 details, with several
   subsections)
3. Conventional method or methods, if applicable
4. Proposed method
5. Experiments (5.1 experimental setup)
6. Results
7. Conclusion
8. Author contribution, Declaration, Acknowledgements, Reference.

For a dataset-based paper the corpus comes right after the Introduction,
because the dataset is the primary contribution. A method plus dataset paper
follows the same order with both parts expanded.

## 6. Corpus or dataset section (dataset-based papers)

- 2.1 Dataset overview: purpose and scope, characteristics, target application
  or domain.
- 2.2 Data collection: sources, procedure, period, inclusion and exclusion
  criteria.
- 2.3 Data preparation: cleaning, preprocessing, filtering, formatting.
- 2.4 Annotation and labeling: annotation methodology, label or class
  definitions, guidelines, annotators, quality control, and inter-annotator
  agreement when applicable.
- 2.5 Dataset characteristics: number of instances, classes or categories,
  feature description, class distribution, statistical characteristics.
- 2.6 Organization and format: file or folder structure, data format,
  metadata, naming conventions, and train/validation/test organization when
  provided.
- 2.7 Validation and quality: quality checking, duplicate detection, missing
  or inconsistent data, label verification, and quality statistics.
- 2.8 Ethical, privacy, and licensing: consent where applicable, privacy and
  anonymization, ethical approval, and data license and usage restrictions.

## 7. Conventional Method

Content the section must cover.

- Baseline method: introduce the conventional or established method, explain
  why it is the baseline, and describe its main components and assumptions.
- Working principle: how the method operates, its processing steps, and the
  relationship between input, intermediate processes, and output.
- Technical formulation: equations, mathematical formulations, parameters,
  and objective functions, with every variable defined clearly.
- Algorithm or procedure: the method as an algorithm or step-by-step
  procedure, with the key computational operations and decisions.
- Main contribution or characteristics: what makes the baseline useful or
  widely applicable.
- Limitations and research gap: the specific weaknesses that motivate the
  proposed method, ending on the gap the proposal addresses.

Recommended flow: conventional method, working principle, mathematical
formulation, algorithm, key characteristics of the baseline, limitations,
research gap, then the proposed method.

Important distinction from the guide: this section is not a second literature
review. The literature review answers 'what have previous researchers done?'
The conventional method section answers 'how does the baseline work
technically, and what limitation motivates the proposed method?'

## 8. Proposed Method

- 3.1 Working principle: the overall mechanism, the input, processing steps,
  and output; how the method differs from the baseline; a flowchart, block
  diagram, or conceptual framework where appropriate.
- 3.2 Technical formulation: the mathematical formulation, with equations,
  parameters, variables, constraints, and objective functions; highlight the
  modification or extension compared with the conventional method.
- 3.3 Algorithm or procedure: a step-by-step procedure with inputs,
  operations, decisions, and outputs, in enough detail to reproduce.
- 3.4 Main contribution: what is new or different, how it addresses the gap,
  the key technical characteristics and expected advantages, and a clear
  boundary between novel parts and adopted parts.

After reading the section, the reader should be able to answer three
questions: what is proposed, how does it work technically, and what is new
compared with the conventional method. Narrative flow: existing method,
limitation, research gap, proposed solution, technical novelty.

## 9. Experiments (method-based paper)

- 4.1 Experimental setup and conditions: hardware, software or platform,
  programming environment, experimental parameters, simulation or
  implementation conditions, and reproducibility settings.
- 4.2 Dataset introduction (method-based papers; dataset-based papers place it
  earlier): source, size, number of classes or features, characteristics,
  distribution, train/validation/test split, and preprocessing.
- 4.3 Experimental procedure: overall workflow, data preparation, application
  of the baseline method, application of the proposed method, training and
  testing procedure, repeated experiments or cross-validation, and
  experimental scenarios.
- 4.4 Parameter configuration: model and method parameters, hyperparameters,
  fixed parameters, optimization settings, and the selection or tuning
  strategy.
- 4.5 Evaluation metrics: accuracy, precision, recall, F1 and similar measures
  where applicable, error and performance measures, mathematical formulation
  of the metrics, and statistical measures when applicable.

Recommended order: 4.1 setup, 4.2 dataset, 4.3 procedure, 4.4 parameters,
4.5 metrics.

## 10. Results

Results are presented and analyzed against the defined evaluation metrics,
because the metrics give the basis for interpretation and comparison.

- 5.1 Results by metric: accuracy-based, precision-based, recall-based,
  F1-based, and so on.
- 5.2 Comparative results: conventional or baseline against the proposed
  method, metric by metric, with improvements and reductions stated.
- 5.3 Ablation study where applicable: remove or replace components and
  measure their contribution.
- 5.4 Statistical analysis: confidence intervals, effect size, t and p
  values.
- 5.5 Discussion of key findings: interpretation of the metric-wise results,
  why the proposed method behaves as it does, and the strengths and
  limitations observed in the experiments.

Recommended flow: metric-wise analysis, comparison, ablation, statistical
validation, findings.

## 11. Conclusion

Content: the research objective or problem, the proposed work and
contribution, the key findings, the research significance, and future work.

Recommended structure: objective, contribution, key findings, significance,
future work. Do not introduce new results, new methods, or new references in
the Conclusion.

## 12. Author contributions

Use the standard contribution roles where they apply: conceptualization,
methodology, software, validation, formal analysis, investigation, resources,
data curation, writing (original draft), writing (review and editing),
visualization, supervision, project administration, and funding acquisition.

## 13. Declaration

The declaration part includes funding, conflict of interest, data
availability, code availability, and an ethical approval statement.

## 14. Acknowledgements

Recognize people and organizations that supported the work but do not qualify
for authorship: technical assistance, research assistance, administrative
support, language or editing support, data or resource providers,
institutional support, funding support when it is not a separate section, and
special assistance.

## 15. References

- Use recent and relevant literature: journal articles, conference papers,
  symposium proceedings, book chapters, and books where appropriate.
- Keep references relevant to the topic and sufficiently up to date.
- Use one consistent citation style throughout; the target venue's
  requirements take precedence over any generic format.
- Avoid unnecessary URLs and link-based references; when a URL is required,
  give the access date if the style asks for it.
- Include full bibliographic information as applicable: authors, title,
  journal, conference or book title, volume, issue, page range, year,
  publisher, and DOI.
- Every in-text citation must appear in the reference list, and every listed
  reference must be cited in the manuscript.
- Verify author names, titles, publication details, DOI, volume, issue, and
  page numbers before submission.

Note from the guide: the checklist phrase about mentioning volume, issue,
pages, date, and publisher is not universal. An IEEE journal reference carries
volume, issue, pages, and year, while a conference paper, book, or book
chapter can have a different structure.

## How the IntentGate paper maps to this guideline

To fill when the draft is audited against this guideline.

