def test_evals(langfuse, make_hr_agent_task):
    golden_dataset = langfuse.get_dataset("ci")

    golden_dataset.run_experiment(
        name="ci-eval",
        task=make_hr_agent_task(),
        evaluators=[keyword_overlap_scorer, exact_match_scorer],
    )
