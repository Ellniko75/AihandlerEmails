from Email import Email
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import transformers
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(
    "./Meta-Llama-3-8B-Instruct")

model = AutoModelForCausalLM.from_pretrained(
    './Meta-Llama-3-8B-Instruct',
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    trust_remote_code=True,
    quantization_config=bnb_config
)


def extractInfo(email: Email):

    messages = [
        {"role": "system", "content": "You are a person who is reading an email of a person interseted in buying or renting a house/apartment, your job is to extract the important data. The email can be either plain text or html"},
        {"role": "user", "content": f"{email.message_data}"},
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = model.generate(
        input_ids,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    response = outputs[0][input_ids.shape[-1]:]
    Email.id_mails_already_processed.append(email.msg_id_data)
    return tokenizer.decode(response, skip_special_tokens=True)
