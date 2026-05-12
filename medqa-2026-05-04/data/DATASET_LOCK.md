# MedQA dataset input lock

The MedQA Jin et al. 2020 4-option test split is the input dataset for every accuracy and paired-test number reported in this run.

## Provenance

- **Source**: Jin, D. et al. 2020, *What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams*. [arXiv:2009.13081](https://arxiv.org/abs/2009.13081)
- **Distribution**: [github.com/jind11/MedQA](https://github.com/jind11/MedQA)
- **Specific file used**: 4-option USMLE test split — `medqa_usmle_4opt_test.jsonl`
- **Number of questions**: 1,273

## SHA-256

```
c3b905ccfa66152dc25afbcb2c10e86c0bdb208824f0658fcdb2c040f60a2beb
```

## Verification command

```bash
shasum -a 256 medqa_usmle_4opt_test.jsonl
# expected:
# c3b905ccfa66152dc25afbcb2c10e86c0bdb208824f0658fcdb2c040f60a2beb  medqa_usmle_4opt_test.jsonl
```

If the SHA-256 does not match, you do not have the same input dataset DNAi used on 2026-05-04, and our numbers may not reproduce.

## Why we do not redistribute

DNAi does not redistribute the raw question text inside this directory because (a) the dataset is already freely available from the original authors at github.com/jind11/MedQA and we prefer that researchers cite the original source, and (b) downloading it yourself confirms that our SHA-256 lock points to the same canonical file in the upstream repository.

The per-question result records in results/*.jsonl reference questions by qid (matching the index in the input file) and store only the gold letter, each arm's predicted letter, parse status, and metadata — enough to bit-exactly reproduce every accuracy and paired-test number reported here without redistribution.
