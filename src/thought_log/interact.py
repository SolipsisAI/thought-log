import re

import torch
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    Conversation,
    ConversationalPipeline,
)

from thought_log.classifier import Classifier
from thought_log.utils import postprocess_text, preprocess_text, load_config


def chat(model, tokenizer, device, classifier=None, max_length: int = 1000):
    """Use model.generate to interact"""
    model.config.pad_token_id = tokenizer.pad_token_id
    model.to(device)

    step = 0

    while True:
        text = input(">> ")
        if text in ["/q", "/quit", "/e", "/exit"]:
            break

        print(f"User: {text}")

        new_user_input_ids = tokenizer.encode(
            preprocess_text(text, classifier=classifier) + tokenizer.eos_token,
            return_tensors="pt",
        ).to(device)

        # append the new user input tokens to the chat history
        bot_input_ids = (
            torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
            if step > 0
            else new_user_input_ids
        )

        # generate chat ids
        chat_history_ids = model.generate(
            bot_input_ids,
            max_length=max_length,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            top_k=100,
            top_p=0.7,
            temperature=0.8,
        )

        response = tokenizer.decode(
            chat_history_ids[:, bot_input_ids.shape[-1] :][0],
            skip_special_tokens=True,
        )

        print(f"Bot: {postprocess_text(response)}")


def chat_pipeline(model, tokenizer, classifier=None, device=None, max_length=1000):
    conversation = Conversation()
    pipe = ConversationalPipeline(
        model=model,
        tokenizer=tokenizer,
        device=-1 if device == "cpu" else device,
    )
    pipe.model.config.pad_token_id = pipe.tokenizer.eos_token_id
    pipe.model.max_length = max_length

    while True:
        text = input(">> ")
        if text in ["/q", "/quit", "/e", "/exit"]:
            break

        conversation.add_user_input(preprocess_text(text, classifier=classifier))

        print(f"User: {text}")

        result = pipe(conversation)
        response = result.generated_responses[-1]

        print(f"Bot: {postprocess_text(response)}")


def interact(
    model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
):
    config_data = load_config()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if not classifier_name:
        classifier_name = config_data["classifier_path"]

    if not model_name:
        model_name = config_data["core_path"]

    if not config_name:
        config_name = model_name

    if not tokenizer_name:
        tokenizer_name = model_name

    config = AutoConfig.from_pretrained(config_name)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, device=device)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        from_tf=False,
        config=config,
    )

    classifier = Classifier(classifier_name, tokenizer=classifier_name, device=device)

    chat_fn = chat_pipeline if pipeline else chat

    chat_fn(
        model, tokenizer, classifier=classifier, device=device, max_length=max_length
    )
