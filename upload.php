<?php
declare(strict_types=1);

define('SELFNAME', 'UPLOAD');
/*
The server-side code should consist of two parts.

1. For IE6-8, Opera, older versions of other browsers you get the file as
you normally do with regular form-base uploads.

2. For browsers which upload file with progress bar, you will need to get the raw
post data and write it to the file.

## Return values ##

You should return json as a text/html, and escape all
'<' as '&lt;', '>' as '&gt;', and '&' as '&amp;'.

Return
{"success":true} when upload was successful
{"error":"error message to display"} in case of error

Send me a mail to andrew (at) valums.com, if you will have any questions.
*/

/**
 * Handle file uploads via XMLHttpRequest
 */
 class qqUploadedFileXhr {
    /**
     * Save the file to the specified path
     * @return boolean TRUE on success
     */
    public function save(string $path): bool {    
        $input = fopen("php://input", "r");
        $temp = tmpfile();
        $realSize = stream_copy_to_stream($input, $temp);
        fclose($input);
        
        if ($realSize !== $this->getSize()){            
            return false;
        }
        
        $target = fopen($path, "w");        
        fseek($temp, 0, SEEK_SET);
        stream_copy_to_stream($temp, $target);
        fclose($target);
        
        return true;
    }

    public function getName(): string {
        return $_GET['qqfile'];
    }

    public function getSize(): int {
        if (isset($_SERVER["CONTENT_LENGTH"])){
            return (int)$_SERVER["CONTENT_LENGTH"];            
        }
        throw new Exception('Getting content length is not supported.');
    }

    public function getPid(): string {
        return $_GET['pid'];
    }
}

class qqUploadedFileForm {
    /**
     * Save the file to the specified path
     * @return boolean TRUE on success
     */
    public function save(string $path): bool {
        return move_uploaded_file($_FILES['qqfile']['tmp_name'], $path);
    }

    public function getName(): string {
        return $_FILES['qqfile']['name'];
    }

    public function getSize(): int {
        return $_FILES['qqfile']['size'];
    }

    public function getPid(): string {
        return $_POST['pid'] ?? '';
    }
}

class qqFileUploader {
    private array $allowedExtensions;
    private int $sizeLimit;
    private qqUploadedFileXhr|qqUploadedFileForm|false $file;

    public function __construct(array $allowedExtensions = [], int $sizeLimit = 10485760) {        
        $this->allowedExtensions = array_map("strtolower", $allowedExtensions);        
        $this->sizeLimit = $sizeLimit;
        
        $this->checkServerSettings();       

        $this->file = match(true) {
            isset($_GET['qqfile']) => new qqUploadedFileXhr(),
            isset($_FILES['qqfile']) => new qqUploadedFileForm(),
            default => false,
        };
    }
    
    private function checkServerSettings(): void {        
        $postSize = $this->toBytes(ini_get('post_max_size'));
        $uploadSize = $this->toBytes(ini_get('upload_max_filesize'));        
        
        if ($postSize < $this->sizeLimit || $uploadSize < $this->sizeLimit){
            $size = max(1, $this->sizeLimit / 1024 / 1024) . 'M';             
            die(json_encode(['error' => "increase post_max_size and upload_max_filesize to $size"]));    
        }        
    }
    
    private function toBytes(string $str): int {
        $val = trim($str);
        $last = strtolower($str[strlen($str)-1]);
        return match($last) {
            'g' => (int)$val * 1024 * 1024 * 1024,
            'm' => (int)$val * 1024 * 1024,
            'k' => (int)$val * 1024,
            default => (int)$val,
        };
    }
    
    /**
     * Returns array('success'=>true) or array('error'=>'error message')
     */
    public function handleUpload(string $uploadDirectory, bool $replaceOldFile = false): array {
        if (!is_writable($uploadDirectory)){
            return ['error' => "Server error. Upload directory isn't writable."];
        }
        
        if (!$this->file){
            return ['error' => 'No files were uploaded.'];
        }
        
        $size = $this->file->getSize();
        
        if ($size == 0) {
            return ['error' => 'File is empty'];
        }
        
        if ($size > $this->sizeLimit) {
            return ['error' => 'File is too large'];
        }
        
        $pathinfo = pathinfo($this->file->getName());
        $filename = $pathinfo['filename'];
        //$filename = md5(uniqid());
        $ext = $pathinfo['extension'];

        if($this->allowedExtensions && !in_array(strtolower($ext), $this->allowedExtensions)){
            $these = implode(', ', $this->allowedExtensions);
            return ['error' => 'File has an invalid extension, it should be one of '. $these . '.'];
        }
        
        //ramdon filename
        $pre_name = dechex((int)($size / 10000));
        $filename = $pre_name . dechex(time());
        $fullname = $filename . '.' . $ext;
        $dir = $uploadDirectory . $this->file->getPid() . '/';
        if(!is_dir($dir)) {
            mkdir($dir, 0775, true);
        }
        if ($this->file->save($dir . $fullname)){
            return [
                'success' => true,
                'filename' => $fullname
            ];
        } else {
            return ['error'=> 'Could not save uploaded file. The upload was cancelled, or server error encountered'];
        }
    }    
}
// list of valid extensions, ex. array("jpeg", "xml", "bmp")
$allowedExtensions = [];
// max file size in bytes, 10M
$sizeLimit = 10 * 1024 * 1024;

$uploader = new qqFileUploader($allowedExtensions, $sizeLimit);
$result = $uploader->handleUpload('uploads/');
// to pass data through iframe you will need to encode all html tags
echo json_encode($result, JSON_UNESCAPED_UNICODE);