#!/usr/bin/env python3
"""
Standalone command line utility for encoding text to German audio using AWS Polly.

Usage:
    python encode_audio.py input.txt [output_dir]
    python encode_audio.py --help
"""

import argparse
import logging
import sys
from pathlib import Path


from langlearn.services.audio import AudioService


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose: If True, enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def read_text_file(file_path: Path) -> str:
    """Read text content from a file.

    Args:
        file_path: Path to the text file

    Returns:
        Content of the text file

    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file can't be decoded as UTF-8
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            raise ValueError("Text file is empty")
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Text file not found: {file_path}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            "utf-8", b"", e.start, e.end, f"Failed to decode file as UTF-8: {e}"
        )


def encode_text_to_audio(
    text: str, output_dir: str = "audio", verbose: bool = False
) -> str:
    """Encode text to German audio using AWS Polly.

    Args:
        text: Text to encode
        output_dir: Directory to save the audio file
        verbose: If True, enable verbose logging

    Returns:
        Path to the generated audio file

    Raises:
        RuntimeError: If audio generation fails
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Initialize audio service with project's default settings
        audio_service = AudioService(
            output_dir=output_dir,
            voice_id="Daniel",  # German male voice
            language_code="de-DE",  # German (Germany)
            speech_rate=67,  # 67% speed (slower)
        )

        logger.info(
            "Generating German audio for text: %s",
            text[:50] + "..." if len(text) > 50 else text,
        )

        # Generate audio file
        audio_file_path = audio_service.generate_audio(text)

        logger.info("Successfully generated audio file: %s", audio_file_path)
        return audio_file_path

    except Exception as e:
        logger.error("Failed to generate audio: %s", str(e))
        raise RuntimeError(f"Audio generation failed: {e}")


def main() -> None:
    """Main entry point for the command line utility."""
    parser = argparse.ArgumentParser(
        description="Encode text to German audio using AWS Polly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python encode_audio.py input.txt
  python encode_audio.py input.txt custom_output_dir
  python encode_audio.py input.txt --verbose
        """,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the text file to encode",
    )

    parser.add_argument(
        "output_dir",
        nargs="?",
        default="audio",
        type=str,
        help="Output directory for audio files (default: 'audio')",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        # Read text from input file
        text = read_text_file(args.input_file)

        # Create output directory if it doesn't exist
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        # Encode text to audio
        audio_file_path = encode_text_to_audio(
            text, output_dir=args.output_dir, verbose=args.verbose
        )

        print(f"✅ Successfully generated audio: {audio_file_path}")
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
