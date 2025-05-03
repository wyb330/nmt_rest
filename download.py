import sys
import os
import argparse
from transformers import AutoModel, AutoTokenizer, AutoConfig, T5ForConditionalGeneration


def download_model(model_name, save_dir=None, use_auth_token=None):
    """
    Hugging Face에서 모델을 다운로드하고 선택적으로 로컬에 저장합니다.

    Args:
        model_name (str): Hugging Face 모델 이름 (예: 'bert-base-uncased', 'gpt2')
        save_dir (str, optional): 모델을 저장할 디렉토리 경로
        use_auth_token (str, optional): 비공개 또는 게이트된 모델에 접근하기 위한 Hugging Face 토큰

    Returns:
        bool: 다운로드 성공 여부
    """
    print(f"모델 '{model_name}' 다운로드 중...")

    try:
        # 모델 설정 정보 다운로드
        print("모델 설정 다운로드 중...")
        config = AutoConfig.from_pretrained(model_name, use_auth_token=use_auth_token)
        print("모델 설정 다운로드 완료")

        # 토크나이저 다운로드
        print("토크나이저 다운로드 중...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=use_auth_token)
            print("토크나이저 다운로드 완료")
        except Exception as e:
            print(f"토크나이저 다운로드 실패: {e}")
            print("일부 모델은 토크나이저가 없을 수 있습니다. 계속 진행합니다.")
            tokenizer = None

        # 모델 다운로드
        print("모델 가중치 다운로드 중... (대용량 파일이므로 시간이 걸릴 수 있습니다)")
        model = T5ForConditionalGeneration.from_pretrained(model_name, use_auth_token=use_auth_token)
        print("모델 가중치 다운로드 완료")

        # 모델 저장 (지정된 경로가 있을 경우)
        if save_dir:
            # 모델명에서 폴더명 추출 (organization/model_name 형식 처리)
            model_folder = model_name.split("/")[-1]
            model_path = os.path.join(save_dir, model_folder)

            os.makedirs(model_path, exist_ok=True)
            print(f"'{model_path}' 경로에 모델 저장 중...")

            config.save_pretrained(model_path)
            print("설정 저장 완료")

            if tokenizer:
                tokenizer.save_pretrained(model_path)
                print("토크나이저 저장 완료")

            model.save_pretrained(model_path)
            print("모델 가중치 저장 완료")

            print(f"모델이 '{model_path}' 경로에 성공적으로 저장되었습니다.")
        else:
            print("저장 경로가 지정되지 않아 모델을 로컬에 저장하지 않았습니다.")

        return True

    except Exception as e:
        print(f"오류 발생: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hugging Face 모델 다운로더')
    parser.add_argument('model_name', type=str, help='다운로드할 Hugging Face 모델 이름')
    parser.add_argument('--save_dir', type=str, default='./models', help='모델을 저장할 디렉토리 경로')
    parser.add_argument('--token', type=str, default=None, help='Hugging Face 인증 토큰 (비공개 모델용)')

    args = parser.parse_args()

    # 모델 다운로드 실행
    success = download_model(args.model_name, args.save_dir, args.token)

    if success:
        print("모델 다운로드가 성공적으로 완료되었습니다.")
    else:
        print("모델 다운로드에 실패했습니다.")
        sys.exit(1)
