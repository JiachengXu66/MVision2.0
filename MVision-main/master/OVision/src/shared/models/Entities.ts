    export class Target {
        constructor(
            public target_id:number, 
            public target_name: string,
            public alt_name: string,
            public creation_date: Date,
            public status_value: 'Active' | 'Complete' | 'Expiring' | 'Error' | 'New' | 'Disabled',
        ) {}
    }

    export class Person extends Target {
        public dob: Date;
        public role: string;
        public age: number;

        constructor(
            target_id:number, 
            target_name: string, 
            alt_name: string, 
            creation_date: Date, 
            status_value: 'Active' | 'Complete' | 'Expiring' | 'Error' | 'New' | 'Disabled',
            dob: Date, 
            role: string) 
            {
            super(target_id, target_name, alt_name, creation_date, status_value);
            this.dob = dob;
            this.role = role;
            this.age = this.getAge(dob);
        }

        public getAge(dob: Date): number {
            const today = new Date();
            const age = today.getFullYear() - dob.getFullYear();
            const month = today.getMonth() - dob.getMonth();
            if (month < 0 || (month === 0 && today.getDate() < dob.getDate())) {
                return age - 1;
            }
            return age;
        }

    }

    export class Location extends Target {
        constructor(
            target_id:number,
            target_name: string,
            alt_name: string,
            creation_date: Date,
            status_value: 'Active' | 'Complete' | 'Expiring' | 'Error' | 'New' | 'Disabled',
            public access: 'public' | 'private' | null)     
            {
            super(target_id,target_name, alt_name, creation_date, status_value);
        }
    }
    
    export class BaseModelConfig {
        constructor(
            public epochs: number,
            public num_frames: number,
            public batch_size: number,
            public train: number,
            public test: number,
            public verification: number,
            public shuffle_size: number
        ) {}
    }
    
    export class Model extends BaseModelConfig {
        constructor(
            public model_id: number,
            public model_name: string,
            epochs: number,
            num_frames: number,
            batch_size: number,
            public creation_date: Date,
            train: number,
            test: number,
            verification: number,
            shuffle_size: number,
            public location_name: string
        ) {
            super(epochs, num_frames, batch_size, train, test, verification, shuffle_size);
        }
    }

    export class ModelConfig extends BaseModelConfig {
        constructor(
            public config_id: number,
            public config_name: string,
            epochs: number,
            num_frames: number,
            batch_size: number,
            train: number,
            test: number,
            verification: number,
            shuffle_size: number
        ) {
            super(epochs, num_frames, batch_size, train, test, verification, shuffle_size);
        }
    }
    
    export class Task extends BaseModelConfig {
        constructor(
            public task_id: number,
            public model_name: string,
            public creation_date: Date,
            public status_value: 'queue' | 'gathering' | 'training' | 'trained' | 'failed',
            public classes: number[],
            public sources: number[],
            epochs: number,
            num_frames: number,
            batch_size: number,
            train: number,
            test: number,
            verification: number,
            shuffle_size: number
        ) {
            super(epochs, num_frames, batch_size, train, test, verification, shuffle_size);
        }
    }

export class Deployment {
    constructor(
        public deployment_id: number,
        public deployment_name: string,
        public target_id: number,
        public status_value: 'Active' | 'Complete' | 'Expiring' | 'Error' | 'New' | 'Disabled',
        public model_id: number,
        public creation_date: Date,
        public start_date: Date,
        public expiry_date: Date,
        public node_id: number,
        public device_id: number
    ){}

    get running_time(): number {
        const currentDate = new Date();
        const startDateMidnight = new Date(this.start_date);
        const expiryDateMidnight = new Date(this.expiry_date);
        startDateMidnight.setHours(0, 0, 0, 0)
        expiryDateMidnight.setHours(0, 0, 0, 0)
        if(currentDate < expiryDateMidnight){
            const timeDiff = currentDate.getTime() - startDateMidnight.getTime();
            const hoursDiff = timeDiff / (1000 * 3600); 
            return Math.floor(hoursDiff); 
        }
        else{
            const timeDiff = expiryDateMidnight.getTime() - startDateMidnight.getTime();
            const hoursDiff = timeDiff / (1000 * 3600); 
            return Math.floor(hoursDiff); 
        }
    }
}

export class Node{
    constructor(        
        public node_id: number,
        public node_name: string,
        public node_address: string,
        public status_value: 'Connected' | 'Disconnected',
        public creation_date: Date
        ){}
}

export class Device{
    constructor(        
        public device_id: number,
        public device_name: string,
        public status_value: 'Connected' | 'Disconnected',
        public creation_date: Date
        ){}
}

export class Report {
    constructor(
        public report_id: number,
        public report_name: string,
        public report_type: string,
        public deployment_id: number,
        public frequency_value: number,
        public frequency_unit: string,
        public creation_date: Date,
        public range_value: number,
        public range_unit: string,
        public graph_id: number,
        public threshold: number
    ) {}
}

export class ReportConfig extends Report {
    constructor(
        report_id: number,
        report_name: string,
        report_type: string,
        deployment_id: number,
        frequency_value: number,
        frequency_unit: string,
        creation_date: Date,
        range_value: number,
        range_unit: string,
        graph_id: number,
        threshold: number,
        public report_classes: number[]
    ) {
        super(report_id, report_name, report_type, deployment_id, frequency_value, frequency_unit, creation_date, range_value, range_unit, graph_id, threshold);
    }
}
