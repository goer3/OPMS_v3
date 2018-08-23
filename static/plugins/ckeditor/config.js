CKEDITOR.editorConfig = function( config ) {
	config.toolbarGroups = [
		{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing', groups: [ 'selection', 'spellchecker', 'find', 'editing' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'styles', groups: [ 'styles' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		{ name: 'tools', groups: [ 'tools' ] },
		{ name: 'others', groups: [ 'others' ] },
		{ name: 'about', groups: [ 'about' ] }
	];

	config.removeButtons = 'BidiLtr,BidiRtl,Anchor,Flash,PageBreak,Iframe,ShowBlocks,About,Indent,Outdent,CreateDiv,Subscript,Superscript,TextField,Textarea,Radio,Select,Button,ImageButton,HiddenField,Scayt,Copy,Paste,PasteText,PasteFromWord,Templates,Save,NewPage,Preview,Print,Cut';
	config.codeSnippet_theme = 'monokai_sublime';
	config.image_previewText = '';
	// 上传图片的 URL
	config.filebrowserImageUploadUrl= "/uploadimg/";
};